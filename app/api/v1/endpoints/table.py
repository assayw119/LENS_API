from fastapi import APIRouter, HTTPException, Depends
from app.db import schemas
from sqlalchemy import text
import logging
from app.db.database import get_session, metadata
from sqlalchemy.orm import Session
from langchain_community.utilities.sql_database import SQLDatabase
from app.core.config import settings

router = APIRouter()

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트


logger = logging.getLogger("uvicorn.error")

# 미들웨어를 거쳐서 왔다는 것은 이미 인증이 완료
# 쿼리 조회는 단순히 테이블 정보만 반환


@router.get("/get_table_list")
async def get_table_list(session: Session = Depends(get_session)):
    tables_info = []
    try:
        for table_name in metadata.tables.keys():
            table_info = {"table_name": table_name}
            table = metadata.tables[table_name]

            table_info["columns"] = []
            for column in table.columns:
                table_info["columns"].append(
                    {"column_name": column.name, "column_type": str(column.type)})
            table_info["primary_key"] = []
            for pk in table.primary_key:
                table_info["primary_key"].append(pk.name)
            table_info["foreign_keys"] = []
            for fk in table.foreign_keys:
                table_info["foreign_keys"].append(fk.target_fullname)
            tables_info.append(table_info)
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        session.close()
        logger.info("Session closed")
    return tables_info
