from fastapi import APIRouter, HTTPException, Depends
from db import schemas
from sqlalchemy import text
from core.llm import run_sql_query
from db.database import get_session
from sqlalchemy.orm import Session

router = APIRouter()
metadata_order = {"name": "Query API Version 1",
                  "description": "Version 1 Query API"}

@router.post("/execute_query")
async def execute_query(input_text: schemas.TextInput):
    query = input_text.text.strip()
    try:
        # SQL 쿼리 실행
        result = run_sql_query(query)
        # 결과를 JSON 형식으로 변환
        # return [dict(row) for row in result]
        return result
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        pass
