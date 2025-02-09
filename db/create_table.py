import psycopg2

from db import DB
from utils.logger import get_logger

logger = get_logger("db_logger")


class CreateDB(DB):
    def create(self):
        conn = self.get_conn()
        cursor = conn.cursor()

        try:
            self.create_post_table(cursor)
            self.create_account_table(cursor)
            conn.commit()

        except Exception as create_error:
            logger.error(f"Error Occurred While Creating"
                         f"Database -> {create_error}")

        finally:
            cursor.close()
            conn.close()

    def create_post_table(self, cursor: psycopg2) -> None:
        post_table_query = """
            CREATE TABLE IF NOT EXISTS posts (
                post_url VARCHAR(255) NOT NULL UNIQUE,
                unique_id VARCHAR(255) NOT NULL UNIQUE PRIMARY KEY,
                content_type BOOLEAN NOT NULL DEFAULT TRUE,
                download_path VARCHAR(255) NOT NULL,
                description TEXT
            );
            """
        cursor.execute(post_table_query)
        logger.info("Post Table Is Created")

    def create_account_table(self, cursor: psycopg2):
        account_table_query = """
            CREATE TABLE IF NOT EXISTS accounts (
                id BIGSERIAL PRIMARY KEY,
                account_name VARCHAR(255) NOT NULL UNIQUE,
                account_url VARCHAR(255) NOT NULL UNIQUE,
                follower_number INT,
                following_scraped BOOLEAN NOT NULL DEFAULT FALSE,
                posts_scraped BOOLEAN NOT NULL DEFAULT FALSE
            );
            """
        cursor.execute(account_table_query)
        logger.info("Account Table Is Created")


if __name__ == '__main__':
    CreateDB().create()