import os

from dotenv import load_dotenv
import psycopg2

from config.config import ROOT_DIR


class DB:
    def __init__(self):
        load_dotenv(f"{ROOT_DIR}/db/.database_env")
        self.db_name = os.getenv("DB_NAME")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT")

    def get_conn(self) -> psycopg2.connect:
        return psycopg2.connect(
            dbname=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )