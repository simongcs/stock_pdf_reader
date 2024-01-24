from src.reports.report_service import ReportService
from src.db.database import Database
from src.pdf_parser.parser import PdfParser
import os
from dotenv import load_dotenv

from src.stocks.stock_service import StockService

load_dotenv()

pdf_folder_path = os.environ["PDF_FOLDER_PATH"]
db_path = os.environ["DB_PATH"]
stocks_path = os.environ["STOCKS_PATH"]

db = Database("sqlite:///" + db_path)
db.create_tables()

stock_service = StockService(db, stocks_path)
stock_service.add_stocks_to_db()
stocks_dict = stock_service.get_stocks_dict()


parser = PdfParser(pdf_folder_path)
report = ReportService(db, parser)
report_dates = report.get_unique_report_dates()

parser.list_new_pdf_files(report_dates)
reports = report.read_reports_from_files(stocks_dict)
report.save_reports(reports)

print("Tabla guardada como CSV ")
