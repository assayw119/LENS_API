from typing import Optional
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, create_engine, Session

# 데이터베이스 파일 이름 지정
database_file = 'user.db'

database_connection_string = f"sqlite:///{database_file}"
connect_args = {"check_same_thread": False}
engine_url = create_engine(database_connection_string, echo=True, connect_args=connect_args)

# Setting config load
class Settings(BaseSettings):
    SECRET_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    class Config:
        env_file = ".env"

# 데이터베이스 테이블 생성하는 함수
def conn():
    SQLModel.metadata.create_all(engine_url)

# Session 사용 후 자동으로 종료
def get_session():
    with Session(engine_url) as session:
        yield session
