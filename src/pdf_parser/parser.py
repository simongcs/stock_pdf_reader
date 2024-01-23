from pandas import DataFrame
from tabula.io import read_pdf
import re
import os
from src.reports.report_model import Report


class PdfParser:
    reports = set()
    new_pdf_files = set()
    stocks_dict = dict()
    report_dates = set()

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def set_stocks(self, stocks):
        self.stocks_dict = {stock.name: stock for stock in stocks}

    def get_unique_report_dates(self, db):
        session = db.get_session()
        dates = session.query(Report.date).distinct().all()
        session.close()
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
            [x[0] + ".pdf" for x in self.report_dates]
        )

    def get_file_data(self, file):
        pdf_path = os.path.join(self.pdf_path, file)
        filename = os.path.splitext(file)[0]
        pdf_date = filename[-8:]
        return pdf_path, pdf_date

    def create_report(self, data, pdf_date, stock):
        return Report(
                    pdf_date,
                    data["Balance (USD)"],
                    data["Número de acciones"],
                    (data["Balance (USD)"] / data["Número de acciones"]),
                    stock.id,
                )

    def get_reports_from_files(self) -> list[Report]:
        reports = []
        for pdf_file in self.new_pdf_files:
            pdf_path, pdf_date = self.get_file_data(pdf_file)
            df = self.pdf_to_df(pdf_path)
            for _, row in df.iterrows():
                reports.append(
                    self.create_report(row, pdf_date,
                                       self.stocks_dict[row["Activo"]])
                )

        return reports

    def save_reports(self, db, reports):
        session = db.get_session()
        session.add_all(reports)
        session.commit()
        session.close()
