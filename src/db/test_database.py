from unittest.mock import patch
import pytest
from src.db.database import Database
from sqlalchemy.orm import Session

@pytest.fixture
def mock_database():
    db = Database("sqlite:///testdata.db")
    return db


def test_create_instance_and_session(mock_database):
    assert isinstance(mock_database, Database)
    assert isinstance(mock_database.get_session(), Session)


def test_create_tables(mock_database):
    with patch("src.db.database.Base.metadata.create_all") as mock_create_all:
        mock_database.create_tables()
        mock_create_all.assert_called_once_with(mock_database.engine)
