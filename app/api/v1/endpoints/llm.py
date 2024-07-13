from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from db import schemas

from app.core.llm import process_message

router = APIRouter()

store = {}


@router.post("/execute_llm")
async def execute_llm(request: schemas.PromptRequest):
    prompt_text = request.prompt
    if not prompt_text:
        return {"error": "No prompt provided."}

    session_id = "1"  # This can be dynamic based on user session management

    response = await process_message(prompt_text, session_id)
    print(response)

    async def generate():
        yield response

    return StreamingResponse(generate(), media_type="text/plain")
