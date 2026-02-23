from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.db.database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    github_username = Column(String(255), unique=True, index=True, nullable=False)
    portfolio_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
