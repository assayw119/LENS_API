from langchain_community.utilities.sql_database import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPExceptions
from fastapi.responses import StreamingResponse
from api import schemas

import inspect
from typing import Union

import mysql.connector
from mysql.connector import Error

# .env파일 로드
load_dotenv()

router = APIRouter(prefix="/llm", tags=["LLM"])


class Settings(BaseSettings):
    API_KEY: str
    API_BASE: str
    DATABASE: str
    DATABASE_HOST: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str


def callLLM():
    settings = Settings()
    API_KEY = settings.API_KEY
    API_BASE = settings.API_BASE

    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key=API_KEY,
        openai_api_base=API_BASE,
    )
    
    memory = ConversationBufferMemory(memory_key="chat_history")
    
    conversation = ConversationChain(
        llm = llm,
        prompt = prompt,
        memory = memory,
        input_key = "question"
    )
    return memory, conversation

def findSQL(answer):
    pattern = r"sql\n(.*?);"
    match = re.search(pattern, answer, re.DOTALL)
    
    if match:
        sql_query = match.group(1)
        return sql_query
    else:
        return -1

async def stream_llm(prompt_text: str):
    db, db_info, db_table_name = callDatabase()
    prompt = makeTemplate()
    prompt.partial(chat_history="쿼리 작성 방법에 대해 알려주세요.")
    memory, conversation = callLLM(prompt)
    
    # Langchain LLM 호출
    answer = await conversation.apredict(question="데이터베이스 정보는 다음과 같습니다. " +
                              db_info + " 테이블명은 다음과 같습니다. " + str(db_table_name) + 
                              " 해당 데이터베이스를 바탕으로 사용자의 질문은 다음과 같습니다. " + prompt_text)  # 비동기로 호출
    answer = json.loads(answer)
    if answer[1]:
        print('-----', answer, '-----')
        print(answer[0], answer[1])

        yield json.dumps(answer[0], ensure_ascii=False)
        yield json.dumps(answer[1], ensure_ascii=False)
    else:
        print('-----', answer, '-----')
        print('Not Query!!')

        yield json.dumps(answer[0], ensure_ascii=False)

    # # SQL 쿼리 추출 및 실행
    # sql_query = findSQL(answer)
    # if sql_query != -1:
    #     try:
    #         # 비동기 쿼리 실행
    #         result = await execute_query(schemas.TextInput(text=sql_query))
    #         yield json.dumps(result)  # JSON 문자열로 변환하여 반환
    #     except HTTPException as e:
    #         yield json.dumps({"error": str(e.detail)})  # JSON 문자열로 변환하여 반환
    # else:
    #     yield json.dumps(answer, ensure_ascii=False)
    #     #yield json.dumps({"error": "No valid SQL query found in the response."})  # JSON 문자열로 변환하여 반환



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
