from sqlalchemy import Column, Integer, String

from src.db.base import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    ticker = Column(String, unique=True)

    def __init__(self, name, ticker):
        self.name = name
        self.ticker = ticker

    def __repr__(self) -> str:
        return f"<Stock(name={self.name}, ticker={self.ticker})>"
