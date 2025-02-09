from typing import Optional

from db import DB
from utils.logger import get_logger

logger = get_logger("db_logger")


class FollowerDB(DB):
    def get_most_follower_user(self) -> Optional[str]:
        self.conn = self.get_conn()
        self.cursor = self.conn.cursor()

        try:
            first_user = self.get_user()
            return first_user

        except Exception as follower_error:
            logger.error(f"Error Occurred While "
                         f"Getting User With The Most Follower Number -> {follower_error}")

        finally:
            self.cursor.close()
            self.conn.close()

    def get_user(self) -> str:
        query = """
        SELECT id, account_url FROM accounts
        ORDER BY following_scraped ASC, follower_number DESC
        LIMIT 1;
        """

        self.cursor.execute(query)
        user_id, account_url = self.cursor.fetchone()
        self.update_scraped_following(user_id)
        return account_url

    def update_scraped_following(self, user_id: int) -> None:
        query_update = """
               UPDATE accounts
               SET following_scraped = True
               WHERE id = %s;
               """
        self.cursor.execute(query_update, (user_id,))
        self.conn.commit()


if __name__ == '__main__':
    print(FollowerDB().get_most_follower_user())