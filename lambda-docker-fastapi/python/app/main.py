from typing import Optional
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from mangum import Mangum
from api.order import router as order_router
from api.database import SessionLocal, engine, Base
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeferredReflection


app = FastAPI(
    title="FastAPI Serverless",
    description="FastAPI를 활용한 서버리스",
    version="0.1.0",
    root_path="/v1",
)

api_router = APIRouter(prefix="/api")

# DeferredReflection을 통해 스키마를 나중에 반영
DeferredReflection.prepare(engine)

@app.get("/")
def read_root():
    return {"Hello": "World~~~"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/test")
async def health_check():
    return {"code": 200, "message": "success", "data": None}

# Dependency
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 데이터베이스에서 데이터 추출
@app.get("/data/")
async def get_data(db: Session = Depends(get_db)):
    try:
        # SQL 쿼리 실행 (text() 함수로 SQL 표현 선언)
        query = text("""
                        SELECT 
                            o.orderNumber,
                            c.customerName,
                            SUM(od.priceEach * od.quantityOrdered) AS totalAmount
                        FROM 
                            orders o
                        JOIN 
                            customers c ON o.customerNumber = c.customerNumber
                        JOIN 
                            orderdetails od ON o.orderNumber = od.orderNumber
                        WHERE 
                            o.status = 'Shipped'
                        GROUP BY 
                            o.orderNumber
                        ORDER BY 
                            totalAmount DESC;
                    """
                    )
        data = db.execute(query).fetchall()
        # 데이터를 튜플의 리스트로 변환하여 반환
        data_list = [tuple(row) for row in data]
        return {"data": data_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")


api_router.include_router(order_router)
app.include_router(api_router)

handler = Mangum(app)