from core.llm import process_message
from fastapi import Request, APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from db.database import get_session
from db.models import Message, Session as SessionModel
import uuid
from datetime import datetime
from typing import List, Optional
import json
from core.store import session_info_store, chat_history_store  # store 모듈을 가져옴
from langchain_core.messages import HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from sqlalchemy.future import select

router = APIRouter()

sql_store = {}


@router.post("/execute_llm")
async def execute_llm(request: Request, session: Session = Depends(get_session), session_id: Optional[str] = None,):
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="사용자 정보를 찾을 수 없습니다.")

    body = await request.body()
    data = json.loads(body)
    prompt = data.get("prompt")
    session_id = data.get("session_id")

    user = request.state.user
    if not session_id:
        use_session = SessionModel(
            user_id=user.id,
            end_time=datetime.now(),
            status="active",
            code=str(uuid.uuid4()),
        )
        session.add(use_session)
        session.commit()

        new_message = Message(
            session_id=use_session.id,
            user_id=user.id,
            message_text=prompt,
            timestamp=datetime.now(),
            sender_type="user",
            message_type="chat",
        )
        session.add(new_message)
        session.commit()

        sql_array = []
        response = await process_message(prompt, session_id, sql_array)

        new_gpt_message = Message(
            session_id=use_session.id,
            user_id=user.id,
            message_text=response,
            timestamp=datetime.now(),
            sender_type="lens",
            message_type="chat",
        )

        session.add(new_gpt_message)
        session.commit()

        # sql_array가 있을 경우에만 db에 저장
        if sql_array:
            for sql in sql_array:
                new_sql_message = Message(
                    session_id=session_obj.id,
                    user_id=user.id,
                    message_text=sql.get("query"),
                    timestamp=datetime.now(),
                    sender_type="lens",
                    message_type="sql",
                )
                session.add(new_sql_message)
                session.commit()

            sql_store[session_id] = sql_array

        session_info_store.set(use_session.code, {
            "user_id": user.id,
            "session_id": use_session.id,
        })

        chat_history_store.set(use_session.id, InMemoryChatMessageHistory(
            messages=[HumanMessage(prompt)]))

        return {"redirect_path": f"/chat/{use_session.code}"}

    # message_type: "chat" | "sql" | "schema";
    # sender_type: "user" | "lens" | "system";

    sql_array = []
    session_obj = session.execute(
        select(SessionModel).filter(SessionModel.code == session_id)
    ).scalars().first()

    new_message = Message(
        session_id=session_obj.id,
        user_id=user.id,
        message_text=prompt,
        timestamp=datetime.now(),
        sender_type="user",
        message_type="chat",
    )
    session.add(new_message)
    session.commit()

    response = await process_message(prompt, session_id, sql_array)

    new_gpt_message = Message(
        session_id=session_obj.id,
        user_id=user.id,
        message_text=response,
        timestamp=datetime.now(),
        sender_type="lens",
        message_type="chat",
    )

    session.add(new_gpt_message)
    session.commit()

    # sql_array가 있을 경우에만 db에 저장
    if sql_array:
        for sql in sql_array:
            new_sql_message = Message(
                session_id=session_obj.id,
                user_id=user.id,
                message_text=sql.get("query"),
                timestamp=datetime.now(),
                sender_type="lens",
                message_type="sql",
            )
            session.add(new_sql_message)
            session.commit()

        sql_store[session_id] = sql_array

    async def generate():
        yield response

    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/sql_history")
async def sql_history(request: Request, session: Session = Depends(get_session), session_id: Optional[str] = None,):

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id를 입력해주세요.")

    # 직전에 실행한 SQL을 가져옴
    sql_array = sql_store.get(session_id, [])

    # store에 저장된 sql을 가져온 후 store에서 삭제
    sql_store[session_id] = []

    return sql_array
