from langchain_community.utilities.sql_database import SQLDatabase
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
import re
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api import schemas
from api.execute_query import execute_query

# .env파일 로드
load_dotenv()

router = APIRouter(prefix="/llm", tags=["LLM"])


class Settings(BaseSettings):
    API_KEY: str
    API_BASE: str


def callDatabase():
    db = SQLDatabase.from_uri("sqlite:///sql_app.db")
    db_info = db.get_table_info()
    db_table_name = db.get_usable_table_names()
    return db, db_info, db_table_name

def makeTemplate():
    template = """
    당신은 10년차 데이터베이스 전문가 입니다. 여러 데이터를 가지고 있으며 사용자는 한 개 혹은 여러 개의 데이터를 조합하여 사용하고 싶어합니다.
    사용자는 데이터사이언티스이며 데이터를 제공받아 새로운 인사이트를 도출하려고 합니다.
    아래 조건에 맞춰 적절한 답변을 해주세요.
    1. 사용자 질문에 알맞는 쿼리를 제공해주세요.
    2. 해당 쿼리가 나오는 이유도 같이 설명해주세요.
    3. 쿼리 실행 결과를 알려주세요.
    
    #대화내용
    {chat_history}
    ----
    사용자: {question}
    엑셀전문가:"""
    prompt = PromptTemplate.from_template(template)
    return prompt

def callLLM(prompt):
    settings = Settings()

    API_KEY = settings.API_KEY
    API_BASE = settings.API_BASE
    
    llm = ChatOpenAI(
        model="gpt-4o",
        openai_api_key = API_KEY,
        openai_api_base = API_BASE,
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
    pattern = r"sql\n(.*?)\n"
    match = re.search(pattern, answer, re.DOTALL)
    
    if match:
        sql_query = match.group(1)
        return sql_query
    else:
        return -1

async def stream_llm(prompt_text: str):
    # db, db_info, db_table_name = callDatabase()
    prompt = makeTemplate()
    prompt.partial(chat_history="쿼리 작성 방법에 대해 알려주세요.")
    memory, conversation = callLLM(prompt)
    
    # Langchain LLM 호출
    answer = await conversation.apredict(question=prompt_text)  # 비동기로 호출
    
    # SQL 쿼리 추출 및 실행
    sql_query = findSQL(answer)
    if sql_query != -1:
        try:
            # 비동기 쿼리 실행
            result = await execute_query(schemas.TextInput(text=sql_query))
            yield json.dumps({"result": result})  # JSON 문자열로 변환하여 반환
        except HTTPException as e:
            yield json.dumps({"error": str(e.detail)})  # JSON 문자열로 변환하여 반환
    else:
        yield json.dumps({"error": "No valid SQL query found in the response."})  # JSON 문자열로 변환하여 반환


@router.post("/execute_llm")
async def execute_llm(request: schemas.PromptRequest):
    # data = await request.json()
    # prompt_text = data.get("prompt")
    prompt_text = request.prompt
    if not prompt_text:
        return {"error": "No prompt provided."}

    return StreamingResponse(stream_llm(prompt_text), media_type="text/plain")