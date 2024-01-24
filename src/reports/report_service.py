import os
from src.pdf_parser.parser import PdfParser
from .report_model import Report


class ReportService:
    def __init__(self, db, parser: PdfParser):
        self.db = db
        self.report_dates = []
        self.parser = parser

    def create_report(self, data, pdf_date, stock):
        return Report(
            pdf_date,
            data["Balance (USD)"],
            data["Número de acciones"],
            (data["Balance (USD)"] / data["Número de acciones"]),
            stock.id,
        )

    def get_unique_report_dates(self) -> list[str]:
        session = self.db.get_session()
        dates = session.query(Report.date).distinct().all()
        session.close()
        return [x[0] for x in dates]

    def read_reports_from_files(self,
                                stocks_dict) -> list[Report]:
        reports = []
        for pdf_file in self.parser.new_pdf_files:
            pdf_path, pdf_date = self.get_file_data(pdf_file)
            df = PdfParser.pdf_to_df(pdf_path)
            for _, row in df.iterrows():
                reports.append(
                    self.create_report(row, pdf_date,
                                       stocks_dict[row["Activo"]])
                )

        return reports

    def get_file_data(self, file):
        pdf_path = os.path.join(self.parser.pdf_folder_path, file)
        filename = os.path.splitext(file)[0]
        pdf_date = filename[-8:]
        return pdf_path, pdf_date

    def save_reports(self, reports):
        session = self.db.get_session()
        session.add_all(reports)
        session.commit()
        session.close()
