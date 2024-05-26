from fastapi import APIRouter, Depends, HTTPException, status
from user.auth.jwt import create_access_token
from user.database.connection import get_session
from user.models.users import User, TokenResponse

user_router = APIRouter(
    tags=["User"],
)

@user_router.post("/login", response_model=TokenResponse)
async def login(body: User, session=Depends(get_session)) -> dict:
    existing_user = session.get(User, body.email)
    try:
        if existing_user:
            access_token = create_access_token(body.email, body.exp)
        else:
            session.add(body)
            session.commit()
            session.refresh(body)
            access_token = create_access_token(body.email, body.exp)
        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad Parameter",
        )
