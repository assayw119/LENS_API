from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProductLineBase(BaseModel):
    productLine: str
    textDescription: Optional[str] = None
    htmlDescription: Optional[str] = None
    image: Optional[bytes] = None


class ProductLineCreate(ProductLineBase):
    pass


class ProductLine(ProductLineBase):
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    productCode: str
    productName: str
    productLine: str
    productScale: str
    productVendor: str
    productDescription: str
    quantityInStock: int
    buyPrice: float
    MSRP: float


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    class Config:
        from_attributes = True


class OfficeBase(BaseModel):
    officeCode: str
    city: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    state: Optional[str] = None
    country: str
    postalCode: str
    territory: str


class OfficeCreate(OfficeBase):
    pass


class Office(OfficeBase):
    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    employeeNumber: int
    lastName: str
    firstName: str
    extension: str
    email: str
    officeCode: str
    reportsTo: Optional[int] = None
    jobTitle: str


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    customerNumber: int
    customerName: str
    contactLastName: str
    contactFirstName: str
    phone: str
    addressLine1: str
    addressLine2: Optional[str] = None
    city: str
    state: Optional[str] = None
    postalCode: Optional[str] = None
    country: str
    salesRepEmployeeNumber: Optional[int] = None
    creditLimit: Optional[float] = None


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    customerNumber: int
    checkNumber: str
    paymentDate: str
    amount: float


class PaymentCreate(PaymentBase):
    pass


class Payment(PaymentBase):
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    orderNumber: int
    orderDate: str
    requiredDate: str
    shippedDate: Optional[str] = None
    status: str
    comments: Optional[str] = None
    customerNumber: int


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    class Config:
        from_attributes = True


class OrderDetailBase(BaseModel):
    orderNumber: int
    productCode: str
    quantityOrdered: int
    priceEach: float
    orderLineNumber: int


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetail(OrderDetailBase):
    class Config:
        from_attributes = True

# 사용자가 입력할 텍스트를 받기 위한 모델 정의


class TextInput(BaseModel):
    text: str

# 프롬프트 모델 정의


class PromptRequest(BaseModel):
    prompt: str


class MessageBase(BaseModel):
    session_id: int
    user_id: int
    message_text: str
    timestamp: datetime
    sender_type: str
    message_type: str

    class Config:
        orm_mode = True


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int

    class Config:
        orm_mode = True
