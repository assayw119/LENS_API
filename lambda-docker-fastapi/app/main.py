from typing import Optional
from fastapi import FastAPI, APIRouter, HTTPException, Depends
from mangum import Mangum
from api import crud, schemas
from api.order import router as order_router
from api.database import SessionLocal, engine, Base
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeferredReflection

from fastapi.middleware.cors import CORSMiddleware # CORS


app = FastAPI(
    title="FastAPI Serverless",
    description="FastAPI를 활용한 서버리스",
    version="0.1.0",
    root_path="/v1",
)

# CORS 정책 설정
origins = [
    "http://localhost:3000",
    "https://lens-one.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

api_router = APIRouter(prefix="/api")

# DeferredReflection을 통해 스키마를 나중에 반영
DeferredReflection.prepare(engine)


# 기본 경로에 대한 루트 엔드포인트
@app.get("/")
def root():
    return {"message": "Hello Fastapi"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/health_check")
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

# API endpoints for ProductLine
@app.post("/productlines/", response_model=schemas.ProductLine)
def create_productline(productline: schemas.ProductLineCreate, db: Session = Depends(get_db)):
    return crud.create_productline(db=db, productline=productline)

@app.get("/productlines/{productline_id}", response_model=schemas.ProductLine)
def read_productline(productline_id: str, db: Session = Depends(get_db)):
    db_productline = crud.get_productline(db=db, productline_id=productline_id)
    if db_productline is None:
        raise HTTPException(status_code=404, detail="Product line not found")
    return db_productline

# API endpoints for Product
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@app.get("/products/{product_code}", response_model=schemas.Product)
def read_product(product_code: str, db: Session = Depends(get_db)):
    db_product = crud.get_product(db=db, product_code=product_code)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# API endpoints for Office
@app.post("/offices/", response_model=schemas.Office)
def create_office(office: schemas.OfficeCreate, db: Session = Depends(get_db)):
    return crud.create_office(db=db, office=office)

@app.get("/offices/{office_code}", response_model=schemas.Office)
def read_office(office_code: str, db: Session = Depends(get_db)):
    db_office = crud.get_office(db=db, office_code=office_code)
    if db_office is None:
        raise HTTPException(status_code=404, detail="Office not found")
    return db_office

# API endpoints for Employee
@app.post("/employees/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db=db, employee=employee)

@app.get("/employees/{employee_number}", response_model=schemas.Employee)
def read_employee(employee_number: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db=db, employee_number=employee_number)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

# API endpoints for Customer
@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

@app.get("/customers/{customer_number}", response_model=schemas.Customer)
def read_customer(customer_number: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db=db, customer_number=customer_number)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# API endpoints for Payment
@app.post("/payments/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return crud.create_payment(db=db, payment=payment)

@app.get("/payments/{customer_number}/{check_number}", response_model=schemas.Payment)
def read_payment(customer_number: int, check_number: str, db: Session = Depends(get_db)):
    db_payment = crud.get_payment(db=db, customer_number=customer_number, check_number=check_number)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

# API endpoints for Order
@app.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@app.get("/orders/{order_number}", response_model=schemas.Order)
def read_order(order_number: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db=db, order_number=order_number)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# API endpoints for OrderDetail
@app.post("/orderdetails/", response_model=schemas.OrderDetail)
def create_orderdetail(orderdetail: schemas.OrderDetailCreate, db: Session = Depends(get_db)):
    return crud.create_orderdetail(db=db, orderdetail=orderdetail)

@app.get("/orderdetails/{order_number}/{product_code}", response_model=schemas.OrderDetail)
def read_orderdetail(order_number: int, product_code: str, db: Session = Depends(get_db)):
    db_orderdetail = crud.get_orderdetail(db=db, order_number=order_number, product_code=product_code)
    if db_orderdetail is None:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return db_orderdetail

# 입력된 SQL 쿼리를 실행하여 결과를 반환하는 엔드포인트
@app.post("/execute_query/")
async def execute_query(input_text: schemas.TextInput):
    # 사용자가 입력한 SQL 쿼리
    # 사용자가 입력한 SQL 쿼리를 줄 단위로 처리하여 하나의 문자열로 결합
    sql_query = input_text.text.strip()

    # 데이터베이스 세션 생성
    db = SessionLocal()

    try:
        # SQL 쿼리 실행
        result = db.execute(text(sql_query))
        # 결과를 리스트로 변환
        result_list = [tuple(row) for row in result]
        return {"data": result_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute SQL query: {str(e)}")
    finally:
        # 데이터베이스 세션 닫기
        db.close()


# # 데이터베이스에서 데이터 추출
# @app.get("/data/")
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


api_router.include_router(order_router)
app.include_router(api_router)

handler = Mangum(app)