from pandas import DataFrame
from tabula.io import read_pdf
import re
import os
from src.reports.report_model import Report
from src.stocks.stock_model import Stock


class PdfParser:
    reports = set()
    new_pdf_files = set()
    stocks = set()
    report_dates = set()

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def set_stocks(self, stocks):
        self.stocks = stocks

    def get_unique_report_dates(self, db):
        session = db.get_session()
        dates = session.query(Report.date).distinct()
        session.close()
        print("dates:", dates)
        self.report_dates = dates

    def pdf_to_df(self, pdf_path) -> DataFrame:
        tables = read_pdf(pdf_path, pages="all", multiple_tables=False)
        df = tables[0]
        df.columns = ["Activo", "x", "Número de acciones", "Balance (USD)"]
        del df["x"]
        df["Balance (USD)"] = df["Balance (USD)"].apply(self.clean_balance)
        return df

    def clean_balance(self, balance) -> float:
        return float(
            re.findall(r"[\d]+[.,\d]+", balance)[0].replace(".", "")
            .replace(",", ".")
        )

    def read_pdf_files(self):
        all_pdf_files = {
            file[-12:] for file in os.listdir(self.pdf_path)
            if file.endswith(".pdf")
        }
        self.new_pdf_files = all_pdf_files - set(
            [x.date + ".pdf" for x in self.report_dates]
        )

    def process_files(self, db, stocks: list[Stock]):
        for pdf_file in self.new_pdf_files:
            pdf_path = os.path.join(self.pdf_path, pdf_file)
            filename = os.path.splitext(pdf_file)[0]
            pdf_date = filename[-8:]
            df = self.pdf_to_df(pdf_path)
            reports = [
                Report(
                    pdf_date,
                    row["Balance (USD)"],
                    row["Número de acciones"],
                    (row["Balance (USD)"] / row["Número de acciones"]),
                    next(
                        (item.id for item in stocks
                         if item.name == row["Activo"]), None
                    ),
                )
                for _, row in df.iterrows()
            ]
            session = db.get_session()
            session.add_all(reports)
            session.commit()
            session.close()
