from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Text, DECIMAL, SmallInteger
from sqlalchemy.orm import relationship

# database.py에서 생성한 Base import
from .database import Base

# Base를 상속 받아 SQLAlchemy model 생성
class ProductLine(Base):
    __tablename__ = "productlines"

    productLine = Column(String(50), primary_key=True)
    textDescription = Column(String(4000))
    htmlDescription = Column(Text)
    image = Column(String(255))  # Assuming mediumblob is stored as a string path

    products = relationship("Product", back_populates="product_line")

class Product(Base):
    __tablename__ = "products"

    productCode = Column(String(15), primary_key=True)
    productName = Column(String(70), nullable=False)
    productLine = Column(String(50), ForeignKey('productlines.productLine'), nullable=False)
    productScale = Column(String(10), nullable=False)
    productVendor = Column(String(50), nullable=False)
    productDescription = Column(Text, nullable=False)
    quantityInStock = Column(Integer, nullable=False)
    buyPrice = Column(DECIMAL(10, 2), nullable=False)
    MSRP = Column(DECIMAL(10, 2), nullable=False)

    product_line = relationship("ProductLine", back_populates="products")

class Office(Base):
    __tablename__ = "offices"

    officeCode = Column(String(10), primary_key=True)
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

    employeeNumber = Column(Integer, primary_key=True)
    lastName = Column(String(50), nullable=False)
    firstName = Column(String(50), nullable=False)
    extension = Column(String(10), nullable=False)
    email = Column(String(100), nullable=False)
    officeCode = Column(String(10), ForeignKey('offices.officeCode'), nullable=False)
    reportsTo = Column(Integer, ForeignKey('employees.employeeNumber'))
    jobTitle = Column(String(50), nullable=False)

    office = relationship("Office", back_populates="employees", foreign_keys=[officeCode])
    reports_to_employee = relationship("Employee", remote_side=[employeeNumber], foreign_keys=[reportsTo])
    customers = relationship("Customer", back_populates="sales_rep_employee")

class Customer(Base):
    __tablename__ = "customers"

    customerNumber = Column(Integer, primary_key=True)
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
    salesRepEmployeeNumber = Column(Integer, ForeignKey('employees.employeeNumber'))
    creditLimit = Column(DECIMAL(precision=10, scale=2))

    sales_rep_employee = relationship("Employee", back_populates="customers")
    payments = relationship("Payment", back_populates="customer")
    orders = relationship("Order", back_populates="customer")

class Payment(Base):
    __tablename__ = "payments"

    customerNumber = Column(Integer, ForeignKey('customers.customerNumber'), primary_key=True)
    checkNumber = Column(String(50), primary_key=True)
    paymentDate = Column(Date, nullable=False)
    amount = Column(DECIMAL(precision=10, scale=2), nullable=False)

    customer = relationship("Customer", back_populates="payments")


class Order(Base):
    __tablename__ = "orders"

    orderNumber = Column(Integer, primary_key=True)
    orderDate = Column(Date, nullable=False)
    requiredDate = Column(Date, nullable=False)
    shippedDate = Column(Date)
    status = Column(String(15), nullable=False)
    comments = Column(Text)
    customerNumber = Column(Integer, ForeignKey('customers.customerNumber'))

    customer = relationship("Customer", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")

class OrderDetail(Base):
    __tablename__ = "orderdetails"

    orderNumber = Column(Integer, ForeignKey('orders.orderNumber'), primary_key=True)
    productCode = Column(String(15), ForeignKey('products.productCode'), primary_key=True)
    quantityOrdered = Column(Integer, nullable=False)
    priceEach = Column(DECIMAL(precision=10, scale=2), nullable=False)
    orderLineNumber = Column(SmallInteger, nullable=False)

    order = relationship("Order", back_populates="order_details")
    product = relationship("Product")  # You may need to define the Product class
