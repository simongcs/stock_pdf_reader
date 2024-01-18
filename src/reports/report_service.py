from .report_model import Report


def get_reports(db):
    session = db.get_session()
    return session.query(Report).all()
    # db.cursor.execute("SELECT date FROM reports")
    # reports = db.cursor.fetchall()
    # return reports


def create_report(db, report_data):
    db.cursor.execute("INSERT INTO reports VALUES (?,?,?,?,?)", report_data)
    db.connection.commit()


def insert_reports(db, reports):
    db.executemany(
        "INSERT INTO reports VALUES (?,?,?,?,?)",
        [report.to_db_tuple() for report in reports],
    )
    db.connection.commit()
