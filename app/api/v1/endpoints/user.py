from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.jwt import create_access_token, create_refresh_token, decode_refresh_token
from app.core.config import settings
from app.db.models import User, TokenResponse, UserBase
from app.db.database import get_session

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: UserBase, session: Session = Depends(get_session)) -> TokenResponse:
    existing_user = session.query(User).filter(
        User.email == body.email).first()

    try:
        if existing_user:
            access_token = create_access_token({"sub": existing_user.id})
            refresh_token = create_refresh_token({"sub": existing_user.id})
        else:
            # 사용자 정보가 없으면 새로운 사용자 생성
            new_user = User(email=body.email,
                            username=body.username, exp=body.exp)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            access_token = create_access_token({"sub": new_user.id})
            refresh_token = create_refresh_token({"sub": new_user.id})

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


@router.post("/logout")
async def logout():
    # 클라이언트에서 토큰을 삭제하도록 지시 (서버 측에서는 특별한 동작이 필요하지 않을 수 있습니다)
    return {"msg": "Successfully logged out"}


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str = Body(...)):
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_id = payload.get("sub")
    new_access_token = create_access_token({"sub": user_id}, expires_delta=timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    new_refresh_token = create_refresh_token(
        {"sub": user_id})  # 새로운 refresh token 생성
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,  # 새로운 refresh token 반환
        "token_type": "Bearer"
    }
