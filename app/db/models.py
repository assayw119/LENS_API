from sqlalchemy import Boolean, Column, ForeignKey, DateTime, Integer, String, Date, Text, DECIMAL, SmallInteger
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel


# database.py에서 생성한 Base import
from .database import Base

# Base를 상속 받아 SQLAlchemy model 생성


class ProductLine(Base):
    __tablename__ = "productlines"

    id = Column(Integer, primary_key=True, autoincrement=True)
    productLine = Column(String(50), unique=True, nullable=False)
    textDescription = Column(String(4000))
    htmlDescription = Column(Text)
    image = Column(String(255))  # Assuming mediumblob is stored as a string path

    products = relationship("Product", back_populates="product_line")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    productCode = Column(String(15), unique=True, nullable=False)
    productName = Column(String(70), nullable=False)
    productLine = Column(Integer, ForeignKey(
        'productlines.id'), nullable=False)
    productScale = Column(String(10), nullable=False)
    productVendor = Column(String(50), nullable=False)
    productDescription = Column(Text, nullable=False)
    quantityInStock = Column(Integer, nullable=False)
    buyPrice = Column(DECIMAL(10, 2), nullable=False)
    MSRP = Column(DECIMAL(10, 2), nullable=False)

    product_line = relationship("ProductLine", back_populates="products")


class Office(Base):
    __tablename__ = "offices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    officeCode = Column(String(10), unique=True, nullable=False)
    city = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    addressLine1 = Column(String(50), nullable=False)
    addressLine2 = Column(String(50))
    state = Column(String(50))
    country = Column(String(50), nullable=False)
    postalCode = Column(String(15), nullable=False)
    territory = Column(String(10), nullable=False)

    employees = relationship("Employee", back_populates="office")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employeeNumber = Column(Integer, unique=True, nullable=False)
    lastName = Column(String(50), nullable=False)
    firstName = Column(String(50), nullable=False)
    extension = Column(String(10), nullable=False)
    email = Column(String(100), nullable=False)
    officeCode = Column(Integer, ForeignKey('offices.id'), nullable=False)
    reportsTo = Column(Integer, ForeignKey('employees.id'))
    jobTitle = Column(String(50), nullable=False)

    office = relationship(
        "Office", back_populates="employees", foreign_keys=[officeCode])
    reports_to_employee = relationship(
        "Employee", remote_side=[id], foreign_keys=[reportsTo])
    customers = relationship("Customer", back_populates="sales_rep_employee")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customerNumber = Column(Integer, unique=True, nullable=False)
    customerName = Column(String(50), nullable=False)
    contactLastName = Column(String(50), nullable=False)
    contactFirstName = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    addressLine1 = Column(String(50), nullable=False)
    addressLine2 = Column(String(50))
    city = Column(String(50), nullable=False)
    state = Column(String(50))
    postalCode = Column(String(15))
    country = Column(String(50), nullable=False)
    salesRepEmployeeNumber = Column(Integer, ForeignKey('employees.id'))
    creditLimit = Column(DECIMAL(precision=10, scale=2))

    sales_rep_employee = relationship("Employee", back_populates="customers")
    payments = relationship("Payment", back_populates="customer")
    orders = relationship("Order", back_populates="customer")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customerNumber = Column(Integer, ForeignKey(
        'customers.id'), nullable=False)
    checkNumber = Column(String(50), nullable=False)
    paymentDate = Column(Date, nullable=False)
    amount = Column(DECIMAL(precision=10, scale=2), nullable=False)

    customer = relationship("Customer", back_populates="payments")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    orderNumber = Column(Integer, unique=True, nullable=False)
    orderDate = Column(Date, nullable=False)
    requiredDate = Column(Date, nullable=False)
    shippedDate = Column(Date)
    status = Column(String(15), nullable=False)
    comments = Column(Text)
    customerNumber = Column(Integer, ForeignKey('customers.id'))

    customer = relationship("Customer", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")


class OrderDetail(Base):
    __tablename__ = "orderdetails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    orderNumber = Column(Integer, ForeignKey('orders.id'), nullable=False)
    productCode = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantityOrdered = Column(Integer, nullable=False)
    priceEach = Column(DECIMAL(precision=10, scale=2), nullable=False)
    orderLineNumber = Column(SmallInteger, nullable=False)

    order = relationship("Order", back_populates="order_details")
    product = relationship("Product")


# User 모델 정의 (이미 존재한다고 가정)
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), nullable=False)
    exp = Column(Integer, nullable=True)

    refresh_tokens = relationship("RefreshToken", back_populates="user")
    sessions = relationship("Session", back_populates="user")
    messages = relationship("Message", back_populates="user")


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="refresh_tokens")

# Session 모델 정의


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    status = Column(String(20), default='active')

    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")

# Message 모델 정의


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message_text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    sender_type = Column(String(20), nullable=False)
    message_type = Column(String(20), nullable=False)

    session = relationship("Session", back_populates="messages")
    user = relationship("User", back_populates="messages")


# Pydantic 모델 정의
class UserBase(BaseModel):
    email: str
    username: str
    exp: int

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
