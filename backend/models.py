from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    # 'admin' or 'manager'
    role = Column(String, default='manager')


class Product(db.Model):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    category = Column(String)
    cost_price = Column(Float)
    selling_price = Column(Float)
    quantity = Column(Integer, default=0)
    safety_stock = Column(Integer, default=0)

    order_items = relationship('OrderItem', back_populates='product')


class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    contact = Column(String)

    orders = relationship('Order', back_populates='supplier')


class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    contact = Column(String)

    orders = relationship('Order', back_populates='customer')


class Order(db.Model):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 'incoming' or 'outgoing'
    order_type = Column(String)
    # ISO date string, e.g. '2024-03-01'
    date = Column(String)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)

    supplier = relationship('Supplier', back_populates='orders')
    customer = relationship('Customer', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)

    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')
