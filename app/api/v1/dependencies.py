from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import ValidationError
from typing import Generator
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db import crud, models, schemas
from app.core.config import settings

security = HTTPBearer()

async def get_db() -> Generator:
    async with SessionLocal() as session:
        yield session


def verify_access_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = schemas.TokenData(**payload)
        if datetime.utcnow() > token_data.exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = crud.get_user(db, user_id=token_data.sub)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = schemas.TokenData(**payload)
        token_record = crud.get_refresh_token(db, token=credentials.credentials)
        if not token_record or token_record.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if datetime.utcnow() > token_data.exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = crud.get_user(db, user_id=token_data.sub)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except (JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )