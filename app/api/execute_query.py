from fastapi import APIRouter, HTTPException
from api import schemas
from sqlalchemy.orm import Session
from api.database import SessionLocal, engine, Base
from sqlalchemy import text
import logging

router = APIRouter(prefix="/query", tags=["Query"])
metadata_order = {"name": "Query API Version 1", "description": "Version 1 Query API"}

logger = logging.getLogger("uvicorn.error")

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트
@router.post("/execute_query")
async def execute_query(input_text: schemas.TextInput):
    sql_query = input_text.text.strip()

    db = SessionLocal()

    try:
        result = db.execute(text(sql_query))
        result_list = [tuple(row) for row in result]
        return {"data": result_list}
    except Exception as e:
        error_message = str(e)
        #logger.error(f"Failed to execute SQL query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail = error_message)
    finally:
        db.close()



# # 데이터베이스에서 데이터 추출
# @router.get("/data/")
# async def get_data(db: Session = Depends(get_db)):
#     try:
#         # SQL 쿼리 실행 (text() 함수로 SQL 표현 선언)
#         query = text("""
#                         SELECT 
#                             o.orderNumber,
#                             c.customerName,
#                             SUM(od.priceEach * od.quantityOrdered) AS totalAmount
#                         FROM 
#                             orders o
#                         JOIN 
#                             customers c ON o.customerNumber = c.customerNumber
#                         JOIN 
#                             orderdetails od ON o.orderNumber = od.orderNumber
#                         WHERE 
#                             o.status = 'Shipped'
#                         GROUP BY 
#                             o.orderNumber
#                         ORDER BY 
#                             totalAmount DESC;
#                     """
#                     )
#         data = db.execute(query).fetchall()
#         # 데이터를 튜플의 리스트로 변환하여 반환
#         data_list = [tuple(row) for row in data]
#         return {"data": data_list}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")
