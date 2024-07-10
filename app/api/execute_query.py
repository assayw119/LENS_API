from fastapi import APIRouter, HTTPException
from app.api import schemas
from app.api.database import database
from sqlalchemy import text
import logging

router = APIRouter(prefix="/query", tags=["Query"])
metadata_order = {"name": "Query API Version 1", "description": "Version 1 Query API"}

logger = logging.getLogger("uvicorn.error")

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트
@router.post("/execute_query")
async def execute_query(input_text: schemas.TextInput):
    sql_query = input_text.text.strip()

    try:
        await database.connect()
        result = await database.fetch_all(query=text(sql_query))
        result_list = [dict(row) for row in result]
        return {"data": result_list}
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        await database.disconnect()
