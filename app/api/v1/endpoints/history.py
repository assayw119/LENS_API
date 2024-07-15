from fastapi import Request, APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
import logging
from db.database import get_async_session, metadata, AsyncSessionLocal
from db.models import Message, Session
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from db import schemas


logger = logging.getLogger(__name__)
router = APIRouter()


def sqlalchemy_obj_to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# messges에서 session_id로 그룹화하여 가져오기


@router.get("/get_chat_history", response_model=List[schemas.Message])
async def get_chat_history(
    request: Request,
    session_id: Optional[str] = Query(None),
    async_session: AsyncSession = Depends(get_async_session)
):
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="사용자 정보를 찾을 수 없습니다.")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id를 입력해주세요.")

    # session_id는 session code로 들어오기 때문에 session 테이블에서 code를 검색하여 id를 가져옴
    user = request.state.user

    async with async_session as session:
        new_session_id = None
        result = await session.execute(
            select(Session).filter(Session.code == session_id)
        )
        session_obj = result.scalars().first()
        if session_obj:
            new_session_id = session_obj.id

        if not new_session_id:
            raise HTTPException(status_code=404, detail="해당 세션을 찾을 수 없습니다.")
        # 최신 메시지 순으로 정렬
        query = select(Message).filter(Message.user_id ==
                                       user.id, Message.session_id == new_session_id).order_by(Message.timestamp.asc())

        result = await session.execute(query)

        messages = result.scalars().all()

    return messages


@router.get("/get_history", response_model=List[schemas.MessageWithSchema])
async def get_history(request: Request, async_session=Depends(get_async_session)):
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="사용자 정보를 찾을 수 없습니다.")

    user = request.state.user

    async with async_session as session:
        # Message에 Session을 조인하고 Session.code로 그룹화하여 가져옴
        # 최종 결과는 Message 객체의 리스트에 Session의 code를 추가한 형태
        result = await session.execute(
            select(Message).join(Session).filter(Message.user_id ==
                                                 user.id).group_by(Session.code).order_by(Message.timestamp.desc())
        )
        messages = result.scalars().all()

        # 각 message를 돌면서 session의 code를 message에 추가
        for message in messages:
            session_select = await session.execute(
                select(Session).filter(Session.id == message.session_id)
            )
            session_obj = session_select.scalars().first()
            message.session_code = session_obj.code

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
                                   user.id, Message.message_type == "sql").order_by(Message.timestamp.desc())
        )
        messages = result.scalars().all()

    # [sqlalchemy_obj_to_dict(message) for message in messages]
    return messages
