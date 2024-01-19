from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from threading import Lock

from src.db.base import Base


class Database:
    _instance: None
    _lock = Lock()
    db_path: str

    def __new__(cls, db_path):
        with cls._lock:
            if not hasattr(cls, "instance"):
                cls._instance = super(Database, cls).__new__(cls)
                cls.engine = create_engine(db_path, echo=True)
                cls.session = sessionmaker(bind=cls.engine)
        return cls._instance

    def get_session(self):
        return self.session()

    @classmethod
    def create_tables(cls):
        Base.metadata.create_all(cls.engine)
