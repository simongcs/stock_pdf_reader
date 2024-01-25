from unittest.mock import patch
import pandas as pd
import pytest
from src.pdf_parser.parser import PdfParser
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


@patch("src.pdf_parser.parser.read_pdf", return_value=[MOCK_PDF_DATAFRAME])
def test_pdf_to_df(mock_read_pdf, parser):
    pdf_dataframe = parser.pdf_to_df("/path")
    mock_read_pdf.assert_called_once()
    assert pdf_dataframe.equals(MOCK_PDF_DATAFRAME)


def test_clean_balance(parser):
    balance = "US $ 1.000,0"
    cleaned_balance = parser.clean_balance(balance)
    assert cleaned_balance == 1000.0


@patch("os.listdir", return_value=[])
def test_list_new_pdf_files_without_reports(mock_os, parser):
    parser.list_new_pdf_files([])
    assert len(parser.new_pdf_files) == 0
    mock_os.assert_called_once()


@patch("os.listdir", return_value=[MOCK_PDF_FILENAME_ONE,
                                   MOCK_PDF_FILENAME_TWO])
def test_list_new_pdf_files_with_reports(mock_os, parserWithReportDates,
                                         parser):
    parser.list_new_pdf_files([MOCK_PDF_FILENAME_TWO[:8]])
    assert parser.new_pdf_files == {MOCK_PDF_FILENAME_ONE}
