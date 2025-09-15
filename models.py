from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Tenant(db.Model):
    __tablename__ = "tenants"
    tenant_id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(100), unique=True, nullable=False)
    api_key = db.Column(db.String(255), nullable=True)
    api_secret = db.Column(db.String(255), nullable=True)
    access_token = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))


class Customer(db.Model):
    __tablename__ = "customers"
    customer_id = db.Column(db.BigInteger, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.tenant_id"), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    total_spent = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    __tablename__ = "products"
    product_id = db.Column(db.BigInteger, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.tenant_id"), nullable=False)
    title = db.Column(db.String(200))
    price = db.Column(db.Numeric(10, 2))
    inventory_quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.BigInteger, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("tenants.tenant_id"), nullable=False)
    customer_id = db.Column(db.BigInteger)
    product_id = db.Column(db.BigInteger)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
