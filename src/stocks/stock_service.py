from src.stocks.stock_model import Stock
import json
from src.db.database import Database


class StockService:
    def __init__(self, db, file_path):
        self.file_path = file_path
        self.db: Database = db

    def get_stocks_dict(self) -> dict[Stock]:
        session = self.db.get_session()
        stocks = session.query(Stock).all()
        session.close()
        return {stock.name: stock for stock in stocks}

    def load_stocks_from_json(self):
        with open(self.file_path, "r") as file:
            data = json.load(file)
            return [Stock(item["name"], item["ticker"])
                    for item in data["stocks"]]

    def add_stocks_to_db(self):
        stocks = self.load_stocks_from_json()
        session = self.db.get_session()
        session.add_all(stocks)
        session.commit()
        session.close()
