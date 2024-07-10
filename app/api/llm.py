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
    db = SQLDatabase.from_uri("sqlite:///./sql_app.db")
    db_info = db.get_table_info()
    db_table_name = db.get_usable_table_names()
    return db, db_info, db_table_name


def makeTemplate():
    template = """
    당신은 매우 유능한 데이터분석가입니다.
    
    먼저 다음의 지시사항을 반드시 준수하세요.
    --- START OF CONDITIONS ---
    - 작업 순서를 반드시 지킬 것.
    - 질문의 의도를 정확히 반영할 것.
    --- END OF CONDITIONS ---
    
    그런 다음 데이터베이스 정보를 확인하세요.
    --- START OF DATABASE INFO ---
    {db_info}
    --- END OF DATABASE INFO ---
    
    이제 사용자의 질문을 확인하고, 순서에 따라 작업을 진행해주세요.
    --- START OF QUESTION ---
    {question}
    --- END OF QUESTION ---
    
    --- START OF TASK ---
    빈 배열이 주어집니다. 이 배열에는 다음의 내용을 순서대로 담아주세요.
    1. 질문이 데이터베이스를 활용해 쿼리를 생성할 수 있다면 쿼리 생성을 위한 전략과 실행시간, 접근방법을 문자열로 배열에 추가 하고 그렇지 않다면 자연스러운 응답을 문자열로 배열에 추가하세요.
    2. 질문이 데이터베이스를 활용해 쿼리를 생성할 수 있다면 생성된 쿼리를 문자열로 배열에 추가하고 그렇지 않으면 빈 문자열을 담아주세요.
    --- END OF TASK ---
    
    작업을 완료하면 배열을 반환해주세요.
    배열외의 내용은 모두 무시됩니다.
    
    백틱(`)을 사용한 코드 블록은 작성하지 마세요.
    오직 배열만 반환해주세요.
    """
    prompt = PromptTemplate.from_template(template)
    return prompt


def callLLM(prompt):
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
        llm=llm, prompt=prompt, memory=memory, input_key="question"
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
    answer = await conversation.predict(
        question="데이터베이스 정보는 다음과 같습니다. "
        + db_info
        + " 테이블명은 다음과 같습니다. "
        + str(db_table_name)
        + " 해당 데이터베이스를 바탕으로 사용자의 질문은 다음과 같습니다. "
        + prompt_text
    )  # 비동기로 호출
    answer = json.loads(answer)
    if answer[1]:
        print("-----", answer, "-----")
        print(answer[0], answer[1])

        yield json.dumps(answer[0], ensure_ascii=False)
        yield json.dumps(answer[1], ensure_ascii=False)
    else:
        print("-----", answer, "-----")
        print("Not Query!!")

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
    # data = await request.json()
    # prompt_text = data.get("prompt")
    prompt_text = request.prompt
    if not prompt_text:
        return {"error": "No prompt provided."}

    return StreamingResponse(stream_llm(prompt_text), media_type="text/plain")
