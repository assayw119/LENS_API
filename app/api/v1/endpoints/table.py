from fastapi import APIRouter, HTTPException, Depends
from app.db import schemas
from sqlalchemy import text
import logging
from app.db.database import get_session, metadata
from sqlalchemy.orm import Session
from langchain_community.utilities.sql_database import SQLDatabase

router = APIRouter()

logger = logging.getLogger("uvicorn.error")

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트


# 미들웨어를 거쳐서 왔다는 것은 이미 인증이 완료
# 쿼리 조회는 단순히 테이블 정보만 반환
@router.get("/get_table_list")
async def get_table_list(session: Session = Depends(get_session)):
    try:
        # 모든 테이블 정보 출력
        # for table_name in metadata.tables.keys():
        #     table = metadata.tables[table_name]
        #     print(f"Table: {table_name}")
        #     for column in table.columns:
        #         print(f"  Column: {column.name}, Type: {column.type}")
        #     # 관계 정보 출력
        #     for fk in table.foreign_keys:
        #         print(f"  Foreign Key: {fk.target_fullname}")
        #     # 인덱스 정보 출력
        #     for index in table.indexes:
        #         print(f"  Index: {index.name}")
        #     # 유니크 제약조건 정보 출력
        #     for constraint in table.constraints:
        #         print(f"  Constraint: {constraint.name}")
        # MariaDB 데이터베이스 URI
        DATABASE_URI = "mysql+mariadbconnector://root:lens@43.202.9.204/db"

        # SQLDatabase 인스턴스 생성
        db = SQLDatabase.from_uri(DATABASE_URI)

        # 테이블 정보 가져오기
        db_info = db.get_table_info()

        # 출력
        print(db_info)
        # SQL 쿼리 실행
        return None
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=400, detail=error_message)
    finally:
        session.close()
        logger.info("Session closed")
