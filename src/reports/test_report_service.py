from unittest.mock import MagicMock, create_autospec, patch
import pandas as pd

import pytest
from src.pdf_parser.parser import PdfParser
from src.db.database import Database
from src.reports.report_model import Report
from src.reports.report_service import ReportService
from src.stocks.stock_model import Stock
from sqlalchemy.orm.session import Session

MOCK_DATE_LIST = ["18-01-24"]
MOCK_PDF_FILENAME_ONE = "27-12-23.pdf"
MOCK_PDF_FILENAME_TWO = "01-01-24.pdf"

MOCK_PDF_DATAFRAME = pd.DataFrame(
    {
        "Activo": ["A1"],
        "x": [1],
        "Número de acciones": [100],
        "Balance (USD)": ["US $ 1.000,0"],
    }
)
MOCK_REPORT = Report(
    MOCK_PDF_FILENAME_ONE[:8],
    MOCK_PDF_DATAFRAME["Balance (USD)"][0],
    MOCK_PDF_DATAFRAME["Número de acciones"][0],
    10,
    1,
)
MOCK_STOCK_DICT = {"A1": {"name": "A1", "ticker": "stck"}}


class TestReportService:

    @pytest.fixture()
    def mock_session(self):
        session = create_autospec(Session)
        session.query().distinct().all.return_value = [MOCK_DATE_LIST]
        session.add_all = MagicMock()
        session.commit = MagicMock()
        session.close = MagicMock()
        return session

    @pytest.fixture()
    def mock_database(self, mock_session):
        database = MagicMock(spec=Database)
        database.get_session.return_value = mock_session
        return database

    @pytest.fixture
    def parser(self) -> PdfParser:
        parser = PdfParser("/path")
        parser.new_pdf_files = {MOCK_PDF_FILENAME_ONE}
        return parser

    @pytest.fixture
    def report_service(self, mock_database, parser):
        return ReportService(mock_database, parser)

    def test_create_report(self, report_service):
        data = {
            "Activo": 1,
            "x": 1,
            "Número de acciones": 100,
            "Balance (USD)": 1000.0,
        }
        pdf_date = MOCK_PDF_FILENAME_ONE[:8]
        stock = Stock("testStock", "testTicker")
        stock.id = 1

        report = report_service.create_report(data, pdf_date, stock)

        assert isinstance(report, Report)
        assert report.stock_id == 1
        assert report.date == pdf_date
        assert report.balance == 1000.0
        assert report.stock_value == 10
        assert report.stock_holding == 100

    def test_get_unique_report_dates(self, report_service):
        dates = report_service.get_unique_report_dates()
        assert dates == MOCK_DATE_LIST

    @patch(
        "src.reports.report_service.ReportService.get_file_data",
        return_value=(
            "/path/{}".format(MOCK_PDF_FILENAME_ONE),
            MOCK_PDF_FILENAME_ONE[:8],
        ),
    )
    @patch("src.pdf_parser.parser.PdfParser.pdf_to_df",
           return_value=MOCK_PDF_DATAFRAME)
    @patch("src.reports.report_service.ReportService.create_report",
           return_value=MOCK_REPORT)
    def test_read_reports_from_files(self, mock_create_report, mock_pdf_to_df,
                                     mock_get_file_data, report_service):
        reports = report_service.read_reports_from_files(MOCK_STOCK_DICT)
        mock_get_file_data.assert_called_once()
        mock_pdf_to_df.assert_called_once()
        mock_create_report.assert_called_once()
        assert reports == [MOCK_REPORT]

    def test_save_reports(self, mock_database, report_service):
        report_service.save_reports({})
        mock_database.get_session.assert_called_once()
        mock_database.get_session().add_all.assert_called_once()
        mock_database.get_session().commit.assert_called_once()

    def test_get_file_data(self, report_service: ReportService):
        file_data = report_service.get_file_data(MOCK_PDF_FILENAME_ONE)
        assert file_data == (
            "/path/{}".format(MOCK_PDF_FILENAME_ONE),
            MOCK_PDF_FILENAME_ONE[:8],
        )
