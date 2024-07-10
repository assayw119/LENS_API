from fastapi import APIRouter, Path, HTTPException, Depends
from app.api import schemas, crud
from sqlalchemy.orm import Session
from app.api.database import SessionLocal, engine, Base
from sqlalchemy.ext.declarative import DeferredReflection


router = APIRouter(prefix="/data", tags=["Data"])
metadata_order = {"name": "Data API Version 1", "description": "Version 1 DATA API"}

# DeferredReflection을 통해 스키마를 나중에 반영
DeferredReflection.prepare(engine)

# Dependency
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API endpoints for ProductLine
@router.post(path="/productlines/", response_model=schemas.ProductLine)
def create_productline(productline: schemas.ProductLineCreate, db: Session = Depends(get_db)):
    return crud.create_productline(db=db, productline=productline)

@router.get(path="/productlines/{productline_id}", response_model=schemas.ProductLine)
def read_productline(productline_id: str, db: Session = Depends(get_db)):
    db_productline = crud.get_productline(db=db, productline_id=productline_id)
    if db_productline is None:
        raise HTTPException(status_code=404, detail="Product line not found")
    return db_productline

# API endpoints for Product
@router.post(path="/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@router.get(path="/products/{product_code}", response_model=schemas.Product)
def read_product(product_code: str, db: Session = Depends(get_db)):
    db_product = crud.get_product(db=db, product_code=product_code)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# API endpoints for Office
@router.post(path="/offices/", response_model=schemas.Office)
def create_office(office: schemas.OfficeCreate, db: Session = Depends(get_db)):
    return crud.create_office(db=db, office=office)

@router.get(path="/offices/{office_code}", response_model=schemas.Office)
def read_office(office_code: str, db: Session = Depends(get_db)):
    db_office = crud.get_office(db=db, office_code=office_code)
    if db_office is None:
        raise HTTPException(status_code=404, detail="Office not found")
    return db_office

# API endpoints for Employee
@router.post(path="/employees/", response_model=schemas.Employee)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    return crud.create_employee(db=db, employee=employee)

@router.get(path="/employees/{employee_number}", response_model=schemas.Employee)
def read_employee(employee_number: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db=db, employee_number=employee_number)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

# API endpoints for Customer
@router.post(path="/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    return crud.create_customer(db=db, customer=customer)

@router.get(path="/customers/{customer_number}", response_model=schemas.Customer)
def read_customer(customer_number: int, db: Session = Depends(get_db)):
    db_customer = crud.get_customer(db=db, customer_number=customer_number)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

# API endpoints for Payment
@router.post(path="/payments/", response_model=schemas.Payment)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return crud.create_payment(db=db, payment=payment)

@router.get(path="/payments/{customer_number}/{check_number}", response_model=schemas.Payment)
def read_payment(customer_number: int, check_number: str, db: Session = Depends(get_db)):
    db_payment = crud.get_payment(db=db, customer_number=customer_number, check_number=check_number)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

# API endpoints for Order
@router.post(path="/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@router.get(path="/orders/{order_number}", response_model=schemas.Order)
def read_order(order_number: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db=db, order_number=order_number)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

# API endpoints for OrderDetail
@router.post(path="/orderdetails/", response_model=schemas.OrderDetail)
def create_orderdetail(orderdetail: schemas.OrderDetailCreate, db: Session = Depends(get_db)):
    return crud.create_orderdetail(db=db, orderdetail=orderdetail)

@router.get(path="/orderdetails/{order_number}/{product_code}", response_model=schemas.OrderDetail)
def read_orderdetail(order_number: int, product_code: str, db: Session = Depends(get_db)):
    db_orderdetail = crud.get_orderdetail(db=db, order_number=order_number, product_code=product_code)
    if db_orderdetail is None:
        raise HTTPException(status_code=404, detail="Order detail not found")
    return db_orderdetail