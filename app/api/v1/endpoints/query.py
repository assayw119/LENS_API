from fastapi import APIRouter, HTTPException
from db import schemas
from db.database import database
from sqlalchemy import text
from api.v1.endpoints.llm import run_sql_query

router = APIRouter()

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트
@router.post("/execute_query")
async def execute_query(query):

    try:
        run_sql_query(query)
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        pass
