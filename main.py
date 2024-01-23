from src.db.database import Database
from src.pdf_parser.parser import PdfParser
import os
from dotenv import load_dotenv

from src.stocks.stock_service import StockService
from src.stocks.stock_model import Stock

load_dotenv()

pdf_folder_path = os.environ["PDF_FOLDER_PATH"]
# csv_folder_path = os.environ["CSV_FOLDER_PATH"]
# processed_files_record = os.environ["PROCESSED_FILES_RECORD"]
db_path = os.environ["DB_PATH"]
stocks_path = os.environ["STOCKS_PATH"]

db = Database("sqlite:///" + db_path)
db.create_tables()

report = PdfParser(pdf_folder_path)
stock_service = StockService(db, stocks_path)
stock_service.add_stocks_to_db()
stocks: list[Stock] = stock_service.get_stocks()

report.set_stocks(stocks)
report.get_unique_report_dates(db)
report.read_pdf_files()
reports = report.get_reports_from_files()
report.save_reports(db, reports)

print("Tabla guardada como CSV ")
