import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# DATABASE_URL = "mariadb+mariadbconnector://root:lens@43.202.9.204/db"

DATABASE_URL = settings.DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    "mariadb+mariadbconnector://root:lens@43.202.9.204/db", echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative class definitions
Base = declarative_base()

# SQLAlchemy 세션 관리 (동기)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 비동기 데이터베이스 연결 설정
metadata = MetaData()
# 메타데이터에 연결된 테이블들 로드
metadata.reflect(bind=engine)


def init_db():
    import app.db.models  # 모델을 가져와야 테이블을 생성할 수 있습니다
    Base.metadata.create_all(bind=engine)
