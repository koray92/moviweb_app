from flask_sqlalchemy import SQLAlchemy
from data_manager_interface import DataManagerInterface
from sqlalchemy import create_engine, text

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        self.db = SQLAlchemy(db_file_name)
        self.engine = create_engine(db_file_name)
