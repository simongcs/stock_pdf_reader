from unittest.mock import MagicMock, create_autospec, patch
import pandas as pd
import pytest
from src.db.database import Database
from src.pdf_parser.parser import PdfParser
from src.stocks.stock_model import Stock
from sqlalchemy.orm.session import Session

MOCK_DATE_LIST = [("18-01-24",)]
MOCK_PDF_DATAFRAME = pd.DataFrame(
    {
        "Activo": ["A1"],
        "x": [1],
        "Número de acciones": [100],
        "Balance (USD)": ["US $ 1000.0"],
    }
)


@pytest.fixture()
def mock_session():
    session = create_autospec(Session)
    session.query().distinct.return_value = MOCK_DATE_LIST
    session.add_all = MagicMock()
    session.commit = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture()
def mock_database(mock_session):
    database = MagicMock(spec=Database)
    database.get_session.return_value = mock_session
    return database


@pytest.fixture
def parser() -> PdfParser:
    return PdfParser("/path")


def test_set_stocks(parser):
    stock = Stock("testStock", "testTicker")
    stock_list = [stock]
    parser.set_stocks(stock_list)
    assert parser.stocks == stock_list


def test_get_unique_reports_dates(mock_database, parser):
    parser.get_unique_report_dates(mock_database)
    assert parser.report_dates == MOCK_DATE_LIST


@patch("src.pdf_parser.parser.read_pdf", return_value=[MOCK_PDF_DATAFRAME])
def test_pdf_to_df(mock_read_pdf, parser):
    pdf_dataframe = parser.pdf_to_df("/path")
    mock_read_pdf.assert_called_once()
    assert pdf_dataframe.equals(MOCK_PDF_DATAFRAME)
