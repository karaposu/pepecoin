# app/models/order.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime


from db.models.base import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, index=True)
    payment_address = Column(String, unique=True)
    amount_due = Column(Float)
    amount_paid = Column(Float, default=0.0)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime)
    order_metadata = Column(JSON)
