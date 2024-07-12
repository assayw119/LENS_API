from typing import Optional
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, create_engine, Session


# Setting config load
class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    

# 환경 변수에서 DATABASE_URL 가져오기
settings = Settings()

# 데이터베이스 URL 설정
database_connection_string = settings.DATABASE_URL
engine_url = create_engine(database_connection_string, echo=True)


# 데이터베이스 테이블 생성하는 함수
def conn():
    SQLModel.metadata.create_all(engine_url)

# Session 사용 후 자동으로 종료
def get_session():
    with Session(engine_url) as session:
        yield session
