import json
from unittest.mock import MagicMock, create_autospec, mock_open, patch
from src.db.database import Database
from src.stocks.stock_service import StockService
from src.stocks.stock_model import Stock
import pytest
from sqlalchemy.orm.session import Session


class TestStockServiceEmpty:
    @pytest.fixture
    def mock_session(self):
        session = create_autospec(Session)
        session.query().all.return_value = []
        session.add_all = MagicMock()
        session.commit = MagicMock()
        session.close = MagicMock()
        return session

    @pytest.fixture
    def mock_database(self, mock_session):
        database = MagicMock(spec=Database)
        database.get_session.return_value = mock_session
        return database

    @pytest.fixture
    def stock_service(self, mock_database):
        return StockService(mock_database, "/path")

    def test_get_empty_stocks_dict(self, stock_service):
        stocks = stock_service.get_stocks_dict()
        assert len(stocks) == 0
        assert stocks == {}


class TestStockService:
    MOCK_STOCK = {"name": "stock", "ticker": "stck"}

    @pytest.fixture
    def mock_session(self):
        session = create_autospec(Session)
        session.query().all.return_value = [
            Stock(**self.MOCK_STOCK)
        ]
        session.add_all = MagicMock()
        session.commit = MagicMock()
        session.close = MagicMock()
        return session

    @pytest.fixture
    def mock_database(self, mock_session):
        database = MagicMock(spec=Database)
        database.get_session.return_value = mock_session
        return database

    @pytest.fixture
    def stock_service(self, mock_database):
        return StockService(mock_database, "/path")

    def test_get_stocks_dict(self, stock_service: StockService):
        stocks = stock_service.get_stocks_dict()
        assert len(stocks) == 1
        assert isinstance(stocks, dict)
        assert stocks["stock"].name == self.MOCK_STOCK["name"]
        assert stocks["stock"].ticker == self.MOCK_STOCK["ticker"]

    def test_load_stocks_from_json(self, stock_service):
        mock_data = {"stocks": [self.MOCK_STOCK]}
        m = mock_open(read_data=json.dumps(mock_data))
        with patch("builtins.open", m):
            stocks = stock_service.load_stocks_from_json()
            assert len(stocks) == 1
            assert stocks[0].name == self.MOCK_STOCK["name"]
            assert stocks[0].ticker == self.MOCK_STOCK["ticker"]
            m.assert_called_once_with("/path", "r")

    def test_add_stocks_to_db(self, stock_service, mock_session,
                              mock_database):
        mock_stocks = [Stock(**self.MOCK_STOCK)]
        with patch.object(
            stock_service, "load_stocks_from_json", return_value=mock_stocks
        ) as mock_load_stocks:
            stock_service.add_stocks_to_db()
            mock_load_stocks.assert_called_once()
            mock_session.add_all.assert_called_once_with(mock_stocks)
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
            mock_database.get_session.assert_called_once()
