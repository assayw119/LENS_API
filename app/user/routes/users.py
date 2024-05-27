from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta

from user.auth.jwt import create_access_token, create_refresh_token, decode_refresh_token
from user.database.connection import get_session
from user.models.users import User, TokenResponse
from user.auth.jwt import settings

user_router = APIRouter(
    tags=["User"],
)

@user_router.post("/login", response_model=TokenResponse)
async def login(body: User, session=Depends(get_session)) -> TokenResponse:
    existing_user = session.get(User, body.email)
    try:
        if existing_user:
            access_token = create_access_token({"sub": body.email})
            refresh_token = create_refresh_token({"sub": body.email})
        else:
            session.add(body)
            session.commit()
            session.refresh(body)
            access_token = create_access_token({"sub": body.email})
            refresh_token = create_refresh_token({"sub": body.email})
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

@user_router.post("/logout")
async def logout():
    # 클라이언트에서 토큰을 삭제하도록 지시 (서버 측에서는 특별한 동작이 필요하지 않을 수 있습니다)
    return {"msg": "Successfully logged out"}

@user_router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Body(...)):
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    email = payload.get("sub")
    new_access_token = create_access_token({"sub": email}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh_token = create_refresh_token({"sub": email})  # 새로운 refresh token 생성
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,  # 새로운 refresh token 반환
        "token_type": "Bearer"
    }
