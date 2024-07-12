from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings  # 설정 파일에서 settings 가져오기

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
