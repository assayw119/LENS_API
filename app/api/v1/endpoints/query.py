from fastapi import APIRouter, HTTPException, Depends
from app.db import schemas
from sqlalchemy import text
<<<<<<< HEAD
from api.v1.endpoints.llm import run_sql_query

router = APIRouter()

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트
@router.post("/execute_query")
async def execute_query(query):
=======
import logging
from app.db.database import get_session
from sqlalchemy.orm import Session

router = APIRouter()
metadata_order = {"name": "Query API Version 1",
                  "description": "Version 1 Query API"}

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트

logger = logging.getLogger("uvicorn.error")

>>>>>>> f41a0249e3fc390b0d04def0b463eee176123291

@router.post("/execute_query")
async def execute_query(input_text: schemas.TextInput, session: Session = Depends(get_session)):
    sql_query = input_text.text.strip()
    try:
<<<<<<< HEAD
        run_sql_query(query)
=======
        # SQL 쿼리 실행
        result = session.execute(text(sql_query))
        # 결과를 JSON 형식으로 변환
        return [dict(row) for row in result]
>>>>>>> f41a0249e3fc390b0d04def0b463eee176123291
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
<<<<<<< HEAD
        pass
=======
        session.close()
        logger.info("Session closed")
>>>>>>> f41a0249e3fc390b0d04def0b463eee176123291
