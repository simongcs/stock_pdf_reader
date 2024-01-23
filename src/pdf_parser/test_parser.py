from unittest.mock import MagicMock, create_autospec, patch
import pandas as pd
import pytest
from src.db.database import Database
from src.pdf_parser.parser import PdfParser
from src.stocks.stock_model import Stock
from sqlalchemy.orm.session import Session
from src.reports.report_model import Report

MOCK_DATE_LIST = [("18-01-24",)]
MOCK_PDF_DATAFRAME = pd.DataFrame(
    {
        "Activo": ["A1"],
        "x": [1],
        "Número de acciones": [100],
        "Balance (USD)": ["US $ 1.000,0"],
    }
)
MOCK_PDF_FILENAME_ONE = "27-12-23.pdf"
MOCK_PDF_FILENAME_TWO = "01-01-24.pdf"
MOCK_REPORT = Report(
    MOCK_PDF_FILENAME_ONE[:8],
    MOCK_PDF_DATAFRAME["Balance (USD)"][0],
    MOCK_PDF_DATAFRAME["Número de acciones"][0],
    10,
    1,
)


@pytest.fixture()
def mock_session():
    session = create_autospec(Session)
    session.query().distinct().all.return_value = MOCK_DATE_LIST
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
    parser = PdfParser("/path")
    parser.stocks_dict = {"A1": "A1"}
    return parser


@pytest.fixture
def parserWithReportDates() -> PdfParser:
    parser = PdfParser("/path")
    parser.report_dates = [(MOCK_PDF_FILENAME_TWO[:-4],)]
    return parser


def test_set_stocks(parser):
    stock = Stock("testStock", "testTicker")
    stock_list = [stock]
    stock_dict = {stock.name: stock for stock in stock_list}
    parser.set_stocks(stock_list)
    assert parser.stocks_dict == stock_dict


def test_get_unique_reports_dates(mock_database, parser):
    parser.get_unique_report_dates(mock_database)
    assert parser.report_dates == MOCK_DATE_LIST


@patch("src.pdf_parser.parser.read_pdf", return_value=[MOCK_PDF_DATAFRAME])
def test_pdf_to_df(mock_read_pdf, parser):
    pdf_dataframe = parser.pdf_to_df("/path")
    mock_read_pdf.assert_called_once()
    assert pdf_dataframe.equals(MOCK_PDF_DATAFRAME)


def test_clean_balance(parser):
    balance = "US $ 1.000,0"
    cleaned_balance = parser.clean_balance(balance)
    assert cleaned_balance == 1000.0


@patch("os.listdir", return_value=[MOCK_PDF_FILENAME_ONE])
def test_read_pdf_files_without_reports(mock_os, parser):
    parser.read_pdf_files()
    assert parser.new_pdf_files == {MOCK_PDF_FILENAME_ONE}


@patch("os.listdir", return_value=[MOCK_PDF_FILENAME_ONE,
                                   MOCK_PDF_FILENAME_TWO])
def test_read_pdf_files_with_reports(mock_os, parserWithReportDates):
    parserWithReportDates.read_pdf_files()
    assert parserWithReportDates.new_pdf_files == {MOCK_PDF_FILENAME_ONE}


def test_get_file_data(parser):
    pdf_path, pdf_date = parser.get_file_data(MOCK_PDF_FILENAME_ONE)
    assert pdf_path == "/path/{}".format(MOCK_PDF_FILENAME_ONE)
    assert pdf_date == MOCK_PDF_FILENAME_ONE[:8]


def test_create_report(parser):
    data = {
        "Activo": 1,
        "x": 1,
        "Número de acciones": 100,
        "Balance (USD)": 1000.0,
    }
    pdf_date = MOCK_PDF_FILENAME_ONE[:8]
    stock = Stock("testStock", "testTicker")
    stock.id = 1

    report = parser.create_report(data, pdf_date, stock)

    assert isinstance(report, Report)
    assert report.stock_id == 1
    assert report.date == pdf_date
    assert report.balance == 1000.0
    assert report.stock_value == 10
    assert report.stock_holding == 100


@patch("src.pdf_parser.parser.PdfParser.get_file_data",
       return_value=("/path/{}"
                     .format(MOCK_PDF_FILENAME_ONE), MOCK_PDF_FILENAME_ONE[:8]
                     ))
@patch("src.pdf_parser.parser.PdfParser.pdf_to_df",
       return_value=MOCK_PDF_DATAFRAME)
@patch("src.pdf_parser.parser.PdfParser.create_report",
       return_value=MOCK_REPORT)
def test_get_reports_from_files(mock_create_report, mock_pdf_to_df,
                                mock_get_file_data, parser):
    parser.new_pdf_files = {MOCK_PDF_FILENAME_ONE}
    parser.get_reports_from_files()
    mock_get_file_data.assert_called_once()
    mock_pdf_to_df.assert_called_once()
    mock_create_report.assert_called_once()


def test_save_reports(parser, mock_database):
    parser.save_reports(mock_database, {})
    mock_database.get_session.assert_called_once()
    mock_database.get_session().add_all.assert_called_once()
    mock_database.get_session().commit.assert_called_once()
