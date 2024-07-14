from core.llm import process_message
from fastapi import Request, APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from db import schemas
from db.database import get_session
from db.models import Message, Session as SessionModel
import uuid
from datetime import datetime

router = APIRouter()

store = {}


@router.post("/execute_llm")
async def execute_llm(request: schemas.PromptRequest, session: Session = Depends(get_session)):
    if not hasattr(request.state, 'user'):
        raise HTTPException(status_code=401, detail="사용자 정보를 찾을 수 없습니다.")

    user = request.state.user
    if not request.session_id:
        # session_id가 없으면 신규 채팅으로 간주
        # session_id를 생성하고 store에 저장
        use_session = SessionModel(
            user_id=user.id,
            end_time=datetime.now(),
            status="active",
            code=uuid.uuid4(),
        )
        session.add(use_session)
        session.commit()

        store[use_session.code] = {
            "user_id": user.id,
            "session_id": use_session.id,
        }

        return {"redirect_path": f"/chat/{use_session.code}"}

    prompt_text = request.prompt
    if not prompt_text:
        return {"error": "No prompt provided."}
    print(f"Prompt: {prompt_text}")
    session_id = "1"  # This can be dynamic based on user session management

    response = await process_message(prompt_text, session_id)
    print(response)

    async def generate():
        yield response

    return StreamingResponse(generate(), media_type="text/plain")
