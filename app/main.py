from fastapi import FastAPI, APIRouter, Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from mangum import Mangum
from contextlib import asynccontextmanager
from jose import JWTError, jwt

from user.routes.users import user_router
from user.database.connection import conn

from api.v1.routers import router as v1_router

from sqlalchemy.orm import Session
from core.config import settings
from db.session import get_session
from db import crud, models, schemas
from datetime import datetime, timedelta
from typing import Generator
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    conn()
    yield
    # Shutdown event (optional)


# CORS
from fastapi.middleware.cors import CORSMiddleware


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
    # 토큰 검증 미들웨어

    # 헤더에 Authorization 필드가 없는 경우
    if "authorization" not in request.headers:
        # 401 Unauthorized
        return JSONResponse(status_code=401, content={"detail": "Authorization header가 필요합니다"})
    
    auth = request.headers["authorization"]
    scheme, _, token = auth.partition(" ")

    if scheme.lower() != "bearer":
        return JSONResponse(status_code=401, content={"detail": "Authorization scheme이 잘못되었습니다"})

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return JSONResponse(status_code=401, content={"detail": "Token payload missing 'sub' field"})
        
        async with get_session() as db:
            user = crud.get_user(db, user_id=user_id)
            if user is None:
                return JSONResponse(status_code=401, content={"detail": "User not found"})

            request.state.user = user
    except JWTError:
        # Access token이 만료된 경우
        if "x-refresh-token" in request.headers:
            refresh_token = request.headers["x-refresh-token"]
            try:
                refresh_payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = refresh_payload.get("sub")
                if user_id is None:
                    return JSONResponse(status_code=401, content={"detail": "Refresh token payload missing 'sub' field"})

                async with get_session() as db:
                    refresh_token_record = crud.get_refresh_token(db, token=refresh_token)
                    if not refresh_token_record or refresh_token_record.is_revoked:
                        return JSONResponse(status_code=401, content={"detail": "Invalid or revoked refresh token"})

                    user = crud.get_user(db, user_id=user_id)
                    if user is None:
                        return JSONResponse(status_code=401, content={"detail": "User not found"})

                    request.state.user = user
            except JWTError:
                return JSONResponse(status_code=401, content={"detail": "Invalid refresh token"})
        else:
            return JSONResponse(status_code=401, content={"detail": "Invalid access token"})

    response = await call_next(request)
    return response

# 기본 경로에 대한 루트 엔드포인트
@app.get("/")
def root():
    return {"message": "Hello Fastapi, last deploy is 2024-07-13"}


# health check
@app.get("/health_check")
async def health_check():
    return {"status": "healthy"}


# API 라우터 등록 V1 prefix
app.include_router(v1_router, prefix="/v1")
app.include_router(user_router, prefix="/user")

handler = Mangum(app)
