from fastapi import Request, APIRouter, HTTPException, Depends
from sqlalchemy import text
import logging
from db.database import get_async_session, metadata, AsyncSessionLocal
from db.models import Message
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from db import schemas

logger = logging.getLogger(__name__)
router = APIRouter()


def sqlalchemy_obj_to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# messges에서 session_id로 그룹화하여 가져오기


@router.get("/get_history", response_model=List[schemas.Message])
async def get_history(request: Request, async_session=Depends(get_async_session)):
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="사용자 정보를 찾을 수 없습니다.")

    user = request.state.user

    # _AsyncGeneratorContextManager에서 실제 AsyncSession 객체를 추출
    async with async_session as session:
        result = await session.execute(
            select(Message).filter(Message.user_id ==
                                   user.id).group_by(Message.session_id)
        )
        messages = result.scalars().all()

    return messages


# messges에서 message_type이 sql인 것만 가져오기
@router.get("/get_sql_history")
async def get_sql_history(request: Request, session: AsyncSession = Depends(get_async_session)):
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="사용자 정보를 찾을 수 없습니다.")

    user = request.state.user

    async with session as async_session:
        result = await async_session.execute(
            select(Message).filter(Message.user_id ==
                                   user.id, Message.message_type == "sql")
        )
        messages = result.scalars().all()

    # [sqlalchemy_obj_to_dict(message) for message in messages]
    return messages
