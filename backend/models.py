from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import sys
import os
sys.path.append(os.path.dirname(__file__))
# Import config and get DATABASE_URL
import config
Base = declarative_base()
engine = create_engine(config.DATABASE_URL, echo=False, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    expected_weight_g = Column(Float, nullable=True)
    inventory = Column(Integer, nullable=False, default=100)
    image_url = Column(String(255), nullable=True)
    # Optional EAN/UPC barcode for high-accuracy matching
    barcode = Column(String(32), unique=True, nullable=True)
class CartItem(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    added_at = Column(DateTime, server_default=func.now())
    weight_verified = Column(Integer, default=0)
    product = relationship("Product")
class TransactionLog(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, server_default=func.now())
    details = Column(String(2000))
    total_amount = Column(Float, nullable=False, default=0.0)
    payment_method = Column(String(50), nullable=True)
    payment_status = Column(String(50), default="pending")

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
