from sqlalchemy import Column, Integer, String

from src.db.base import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    balance = Column(Integer)
    stock_holding = Column(Integer)
    stock_value = Column(Integer)
    stock_id = Column(Integer)

    def __init__(self, date, balance, stock_holding, stock_value, stock_id):
        self.date = date
        self.balance = balance
        self.stock_holding = stock_holding
        self.stock_value = stock_value
        self.stock_id = stock_id

    def __repr__(self):
        return (
            "<Report(date='%s', balance='%s', stock_holding='%s',\
              stock_value='%s', stock_id='%s')>"
            % (
                self.date,
                self.balance,
                self.stock_holding,
                self.stock_value,
                self.stock_id,
            )
        )
