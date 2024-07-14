from fastapi import APIRouter, HTTPException, Depends
from app.db import schemas
from sqlalchemy import text
import logging
from app.db.database import get_session
from sqlalchemy.orm import Session

router = APIRouter()
metadata_order = {"name": "Query API Version 1",
                  "description": "Version 1 Query API"}

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트

logger = logging.getLogger("uvicorn.error")


@router.post("/execute_query")
async def execute_query(input_text: schemas.TextInput, session: Session = Depends(get_session)):
    sql_query = input_text.text.strip()
    if not sql_query:
        raise HTTPException(status_code=400, detail="SQL 쿼리를 입력해주세요.")

    try:
        result = session.execute(text(sql_query))
        rows = result.fetchall()

        # SQLAlchemy Row 객체를 딕셔너리로 변환
        results_list = []
        for row in rows:
            row_dict = dict(row._mapping)  # _mapping을 사용하여 올바르게 변환
            results_list.append(row_dict)

        print(results_list)
        return results_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
