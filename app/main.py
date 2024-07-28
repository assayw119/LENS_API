from fastapi import FastAPI, APIRouter, Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum
from contextlib import asynccontextmanager
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
from sqlalchemy.future import select

from api.v1.routers import router as v1_router
from core.config import settings
from db.database import init_db, get_async_session
from db.models import User, RefreshToken


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    init_db()
    yield
    # Shutdown event (optional)

app = FastAPI(
    title="FastAPI Serverless",
    description="FastAPI를 활용한 서버리스",
    version="0.1.0",
    lifespan=lifespan,
)

security = HTTPBearer()

# CORS 정책 설정
origins = [
    "http://localhost:3000",
    "https://lens-one.vercel.app",
    "https://www.lensql.chat",
    "https://api.lensql.chat",
    "http://lens-server-load-balancer-486960209.ap-northeast-2.elb.amazonaws.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 미들웨어 정의

@app.middleware("http")
async def verify_token_middleware(request: Request, call_next):
    # 프리플라이트 요청 확인 및 허용
    if request.method == "OPTIONS":
        return await call_next(request)

    # Swagger UI와 ReDoc에 대한 요청은 토큰 검증을 건너 뛰기
    if request.url.path in ["/",
                            "/docs",
                            "/docs/oauth2-redirect",
                            "/redoc",
                            "/openapi.json",
                            "/health_check",
                            "/v1/user/login",
                            "/v1/user/token/refresh",
                            ]:
        return await call_next(request)

    # 토큰 검증 미들웨어
    if "authorization" not in request.headers:
        return JSONResponse(status_code=401, content={"detail": "Authorization header가 필요합니다"})

    auth = request.headers["authorization"]
    scheme, _, token = auth.partition(" ")

    if scheme.lower() != "bearer":
        return JSONResponse(status_code=401, content={"detail": "Authorization scheme이 잘못되었습니다"})
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])

        user_id = payload.get("sub")
        if user_id is None:
            return JSONResponse(status_code=401, content={"detail": "페이로드에 'sub' 필드가 누락되었습니다."})

        async with get_async_session() as db:
            result = await db.execute(select(User).filter(User.id == int(user_id)))
            user = result.scalars().first()
            if user is None:
                return JSONResponse(status_code=401, content={"detail": "유저를 찾을 수 없습니다."})
            request.state.user = user
    except JWTError as e:
        # Access token이 만료된 경우
        if "x-refresh-token" in request.headers:
            refresh_token = request.headers["x-refresh-token"]
            try:
                refresh_payload = jwt.decode(
                    refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = refresh_payload.get("sub")
                if user_id is None:
                    return JSONResponse(status_code=401, content={"detail": "refresh token 페이로드에 'sub' 필드가 누락되었습니다."})

                async with get_async_session() as db:
                    result = await db.execute(select(RefreshToken).filter(RefreshToken.user_id == user_id))
                    refresh_token_record = result.scalars().first()
                    if not refresh_token_record or refresh_token_record.is_revoked:
                        return JSONResponse(status_code=401, content={"detail": "유효하지 않거나 취소된 refresh token입니다."})

                    result = await db.execute(select(User).filter(User.id == user_id))
                    user = result.scalars().first()
                    if user is None:
                        return JSONResponse(status_code=401, content={"detail": "유저를 찾을 수 없습니다."})

            except JWTError:
                return JSONResponse(status_code=401, content={"detail": "refresh token이 유효하지 않습니다."})
        else:
            return JSONResponse(status_code=401, content={"detail": "Access token이 만료되었습니다."})

    response = await call_next(request)
    return response


@app.get("/")
def root():
    return {"message": "Hello Fastapi v32, last deploy is 2024-07-18"}

# health check


@app.get("/health_check")
async def health_check():
    return {"status": "healthy"}

# API 라우터 등록 V1 prefix
app.include_router(v1_router, prefix="/v1")

handler = Mangum(app)
