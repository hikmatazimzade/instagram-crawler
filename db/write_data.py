from typing import List, Tuple, Dict

from psycopg2.extras import execute_values

from db import DB
from utils.logger import get_logger

logger = get_logger("db_logger")


def add_unique_id(post_insert_data: List[List]) -> None:
    for post in post_insert_data:
        post_url = post[0]
        unique_id = post_url.rstrip("/").split("/")[-1]
        post.insert(1, unique_id)


def add_account_url(account_insert_data: List[List]) -> None:
    for account in account_insert_data:
        account_url = f"https://www.instagram.com/{account[0]}/"
        account.insert(1, account_url)


def add_posts_scraped(account_insert_data: List[List]) -> None:
    for account in account_insert_data:
        account.append(True)


class WriteDB(DB):
    def write(self, account_data: Dict[Tuple[str, int], Dict[str, List]]):
        self.conn = self.get_conn()
        self.cursor = self.conn.cursor()

        try:
            for curr_account in account_data:
                account_name, follower = curr_account
                curr_post_data = account_data[curr_account]
                post_insert_data = [[post_url] + curr_post_data[post_url]
                                    for post_url in curr_post_data]
                add_unique_id(post_insert_data)
                self.write_post_data(post_insert_data)
                logger.info(f"Written {account_name} Posts Data To Database!")

            account_insert_data = [list(account) for account in account_data]
            add_account_url(account_insert_data)
            add_posts_scraped(account_insert_data)
            self.write_account_data(account_insert_data)

        except Exception as write_error:
            logger.error(f"Error Occurred While "
                         f"Writing Post Data To Database -> {write_error}")

        finally:
            self.cursor.close()
            self.conn.close()

    def write_post_data(self,post_insert_data: List[List]):
        insert_query = """
            INSERT INTO posts (post_url, unique_id,
            content_type, download_path, description) 
            VALUES %s
            ON CONFLICT (unique_id) DO NOTHING
        """
        execute_values(self.cursor, insert_query, post_insert_data)
        self.conn.commit()

    def write_account_data(self, account_data: List[List]):
        insert_query = """
            INSERT INTO accounts (account_name, account_url,
            follower_number, posts_scraped) 
            VALUES %s
            ON CONFLICT (account_url) DO NOTHING
        """

        execute_values(self.cursor, insert_query, account_data)
        self.conn.commit()

        account_names = [a[0] for a in account_data]
        logger.info(f"Written Accounts Data To Database With {account_names}")