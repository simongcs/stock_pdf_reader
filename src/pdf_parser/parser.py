import os
import re
from tabula.io import read_pdf
from pandas import DataFrame


class PdfParser:
    reports = set()
    new_pdf_files = set()
    stocks_dict = dict()
    report_dates = set()

    def __init__(self, pdf_folder_path):
        self.pdf_folder_path = pdf_folder_path

    @classmethod
    def pdf_to_df(self, pdf_path) -> DataFrame:
        tables = read_pdf(pdf_path, pages="all", multiple_tables=False)
        df = tables[0]
        df.columns = ["Activo", "x", "Número de acciones", "Balance (USD)"]
        del df["x"]
        df["Balance (USD)"] = df["Balance (USD)"].apply(self.clean_balance)
        return df

    @classmethod
    def clean_balance(self, balance) -> float:
        return float(
            re.findall(r"[\d]+[.,\d]+", balance)[0].replace(".", "")
            .replace(",", ".")
        )

    def list_new_pdf_files(self, report_dates):
        all_pdf_files = {
            file[-12:] for file in os.listdir(self.pdf_folder_path)
            if file.endswith(".pdf")
        }
        self.new_pdf_files = all_pdf_files - set(
            [x + ".pdf" for x in report_dates]
        )
