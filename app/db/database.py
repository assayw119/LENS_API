import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from core.config import settings

DATABASE_URL = settings.DATABASE_URL
# 비동기 데이터베이스 URL 구성
ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "mariadb+mariadbconnector", "mysql+aiomysql")

# 동기 SQLAlchemy 엔진 및 세션 설정
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base()

# 동기 세션 생성 함수


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 비동기 SQLAlchemy 엔진 및 세션 설정
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 비동기 세션 생성 함수


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# 비동기 데이터베이스 연결 설정
metadata = MetaData()
metadata.reflect(bind=engine)


def init_db():
    import db.models  # 모델을 가져와야 테이블을 생성할 수 있습니다
    Base.metadata.create_all(bind=engine)
