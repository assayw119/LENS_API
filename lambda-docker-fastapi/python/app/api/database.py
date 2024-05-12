import json
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SECRET_FILE = os.path.join(BASE_DIR, 'database.json')
# secrets = json.loads(open(SECRET_FILE).read())
# db = secrets["DB"]

## SQLAlchemy 사용할 DB URL 생성하기
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{db.get('user')}:{db.get('password')}@{db.get('host')}:{db.get('port')}/{db.get('database')}?charset=utf8"

## SQLAlchemy engine 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

## DB 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

## Base class 생성
Base = declarative_base()