from fastapi import FastAPI, APIRouter
from mangum import Mangum
from contextlib import asynccontextmanager

# API
from app.api.order import router as data_router
from app.api.execute_query import router as query_router
from app.user.routes.users import user_router
from app.user.database.connection import conn
from app.api.llm import router as llm_router


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


api_router = APIRouter(prefix="/api")


# 기본 경로에 대한 루트 엔드포인트
@app.get("/")
def root():
    return {"message": "Hello Fastapi v5!"}


# health check
@app.get("/health_check")
async def health_check():
    return {"status": "healthy"}


api_router.include_router(data_router)
api_router.include_router(query_router)
api_router.include_router(user_router)
api_router.include_router(llm_router)
app.include_router(api_router)

handler = Mangum(app)
