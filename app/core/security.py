from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db import models, schemas

def create_refresh_token(db: Session, user_id: int, token: str, expires_in: int):
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    db_token = models.RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def revoke_refresh_token(db: Session, token: str):
    db_token = db.query(models.RefreshToken).filter(models.RefreshToken.token == token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
    return db_token

def get_refresh_token(db: Session, token: str):
    return db.query(models.RefreshToken).filter(models.RefreshToken.token == token, models.RefreshToken.is_revoked == False).first()

def delete_expired_tokens(db: Session):
    now = datetime.utcnow()
    db.query(models.RefreshToken).filter(models.RefreshToken.expires_at < now).delete()
    db.commit()
