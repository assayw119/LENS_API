from sqlalchemy.orm import Session
from db import models, schemas

# Create
def create_productline(db: Session, productline: schemas.ProductLineCreate):
    db_productline = models.ProductLine(**productline.dict())
    db.add(db_productline)
    db.commit()
    db.refresh(db_productline)
    return db_productline

def create_product(db: Session, product: schemas.ProductCreate):
    db_product = models.Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def create_office(db: Session, office: schemas.OfficeCreate):
    db_office = models.Office(**office.dict())
    db.add(db_office)
    db.commit()
    db.refresh(db_office)
    return db_office

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def create_customer(db: Session, customer: schemas.CustomerCreate):
    db_customer = models.Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def create_orderdetail(db: Session, orderdetail: schemas.OrderDetailCreate):
    db_orderdetail = models.OrderDetail(**orderdetail.dict())
    db.add(db_orderdetail)
    db.commit()
    db.refresh(db_orderdetail)
    return db_orderdetail

# Read
def get_productline(db: Session, productline_id: str):
    return db.query(models.ProductLine).filter(models.ProductLine.productLine == productline_id).first()

def get_product(db: Session, product_code: str):
    return db.query(models.Product).filter(models.Product.productCode == product_code).first()

def get_office(db: Session, office_code: str):
    return db.query(models.Office).filter(models.Office.officeCode == office_code).first()

def get_employee(db: Session, employee_number: int):
    return db.query(models.Employee).filter(models.Employee.employeeNumber == employee_number).first()

def get_customer(db: Session, customer_number: int):
    return db.query(models.Customer).filter(models.Customer.customerNumber == customer_number).first()

def get_payment(db: Session, customer_number: int, check_number: str):
    return db.query(models.Payment).filter(models.Payment.customerNumber == customer_number, models.Payment.checkNumber == check_number).first()

def get_order(db: Session, order_number: int):
    return db.query(models.Order).filter(models.Order.orderNumber == order_number).first()

def get_orderdetail(db: Session, order_number: int, product_code: str):
    return db.query(models.OrderDetail).filter(models.OrderDetail.orderNumber == order_number, models.OrderDetail.productCode == product_code).first()

# Update
def update_productline(db: Session, productline_id: str, productline: schemas.ProductLineCreate):
    db_productline = db.query(models.ProductLine).filter(models.ProductLine.productLine == productline_id).first()
    db_productline.textDescription = productline.textDescription
    db_productline.htmlDescription = productline.htmlDescription
    db_productline.image = productline.image
    db.commit()
    return db_productline

def update_product(db: Session, product_code: str, product: schemas.ProductCreate):
    db_product = db.query(models.Product).filter(models.Product.productCode == product_code).first()
    db_product.productName = product.productName
    # Update other fields similarly
    db.commit()
    return db_product

def update_office(db: Session, office_code: str, office: schemas.OfficeCreate):
    db_office = db.query(models.Office).filter(models.Office.officeCode == office_code).first()
    db_office.city = office.city
    # Update other fields similarly
    db.commit()
    return db_office

def update_employee(db: Session, employee_number: int, employee: schemas.EmployeeCreate):
    db_employee = db.query(models.Employee).filter(models.Employee.employeeNumber == employee_number).first()
    db_employee.lastName = employee.lastName
    # Update other fields similarly
    db.commit()
    return db_employee

def update_customer(db: Session, customer_number: int, customer: schemas.CustomerCreate):
    db_customer = db.query(models.Customer).filter(models.Customer.customerNumber == customer_number).first()
    db_customer.customerName = customer.customerName
    # Update other fields similarly
    db.commit()
    return db_customer

def update_payment(db: Session, customer_number: int, check_number: str, payment: schemas.PaymentCreate):
    db_payment = db.query(models.Payment).filter(models.Payment.customerNumber == customer_number, models.Payment.checkNumber == check_number).first()
    db_payment.paymentDate = payment.paymentDate
    # Update other fields similarly
    db.commit()
    return db_payment

def update_order(db: Session, order_number: int, order: schemas.OrderCreate):
    db_order = db.query(models.Order).filter(models.Order.orderNumber == order_number).first()
    db_order.orderDate = order.orderDate
    # Update other fields similarly
    db.commit()
    return db_order

def update_orderdetail(db: Session, order_number: int, product_code: str, orderdetail: schemas.OrderDetailCreate):
    db_orderdetail = db.query(models.OrderDetail).filter(models.OrderDetail.orderNumber == order_number, models.OrderDetail.productCode == product_code).first()
    db_orderdetail.quantityOrdered = orderdetail.quantityOrdered
    # Update other fields similarly
    db.commit()
    return db_orderdetail

# Delete
def delete_productline(db: Session, productline_id: str):
    db_productline = db.query(models.ProductLine).filter(models.ProductLine.productLine == productline_id).first()
    if db_productline:
        db.delete(db_productline)
        db.commit()
        return True
    return False

def delete_product(db: Session, product_code: str):
    db_product = db.query(models.Product).filter(models.Product.productCode == product_code).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False

def delete_office(db: Session, office_code: str):
    db_office = db.query(models.Office).filter(models.Office.officeCode == office_code).first()
    if db_office:
        db.delete(db_office)
        db.commit()
        return True
    return False

def delete_employee(db: Session, employee_number: int):
    db_employee = db.query(models.Employee).filter(models.Employee.employeeNumber == employee_number).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False

def delete_customer(db: Session, customer_number: int):
    db_customer = db.query(models.Customer).filter(models.Customer.customerNumber == customer_number).first()
    if db_customer:
        db.delete(db_customer)
        db.commit()
        return True
    return False

def delete_payment(db: Session, customer_number: int, check_number: str):
    db_payment = db.query(models.Payment).filter(models.Payment.customerNumber == customer_number, models.Payment.checkNumber == check_number).first()
    if db_payment:
        db.delete(db_payment)
        db.commit()
        return True
    return False

def delete_order(db: Session, order_number: int):
    db_order = db.query(models.Order).filter(models.Order.orderNumber == order_number).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False

def delete_orderdetail(db: Session, order_number: int, product_code: str):
    db_orderdetail = db.query(models.OrderDetail).filter(models.OrderDetail.orderNumber == order_number, models.OrderDetail.productCode == product_code).first()
    if db_orderdetail:
        db.delete(db_orderdetail)
        db.commit()
        return True
    return False
