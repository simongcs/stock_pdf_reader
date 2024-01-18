import json
from unittest.mock import MagicMock, create_autospec, mock_open, patch
from src.db.database import Database
from src.stocks.stock_service import StockService
from src.stocks.stock_model import Stock
import pytest
from sqlalchemy.orm.session import Session


@pytest.fixture
def mock_session():
    session = create_autospec(Session)
    session.query().all.return_value = []
    session.add_all = MagicMock()
    session.commit = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def mock_database(mock_session):
    database = MagicMock(spec=Database)
    database.get_session.return_value = mock_session
    return database


@pytest.fixture
def stock_service(mock_database):
    return StockService(mock_database, "/path")


@pytest.fixture
def mock_open_file():
    return MagicMock(spec=open)


def test_can_get_empty_stocks(stock_service):
    stocks = stock_service.get_stocks()
    assert len(stocks) == 0


def test_load_stocks_from_json(stock_service):
    mock_data = {"stocks": [{"name": "name", "ticker": "symbol"}]}
    m = mock_open(read_data=json.dumps(mock_data))
    with patch("builtins.open", m):
        stocks = stock_service.load_stocks_from_json()
        assert len(stocks) == 1
        m.assert_called_once_with("/path", "r")


def test_add_stocks_to_db(stock_service, mock_session, mock_database):
    mock_stocks = [Stock(name="name", ticker="symbol")]
    with patch.object(
        stock_service, "load_stocks_from_json", return_value=mock_stocks
    ) as mock_load_stocks:
        stock_service.add_stocks_to_db()
        mock_load_stocks.assert_called_once()
        mock_session.add_all.assert_called_once_with(mock_stocks)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_database.get_session.assert_called_once()

