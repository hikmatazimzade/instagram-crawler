from typing import List, Tuple, Dict

from db import DB
from utils.logger import get_logger

logger = get_logger("db_logger")


class UpdateDB(DB):
    def update(self, account_data: Dict[Tuple[str, int], Dict[str, List]]) -> None:
        self.conn = self.get_conn()
        self.cursor = self.conn.cursor()

        try:
            account_names = [account[0] for account in account_data]
            self.make_update(account_names)

        except Exception as write_error:
            logger.error(f"Error Occurred While "
                         f"Writing Post Data To Database -> {write_error}")

        finally:
            self.cursor.close()
            self.conn.close()

    def make_update(self, account_names: List[str]) -> None:
        update_query = """
            UPDATE accounts
            SET posts_scraped = TRUE
            WHERE account_name = ANY(%s)
        """
        try:
            self.cursor.execute(update_query, (account_names,))
            self.conn.commit()
            logger.info(f"Successfully Updated posts_scraped Values For"
                        f"{account_names} Accounts")

        except Exception as update_error:
            logger.error(f"An Error Occurred While Updating {account_data}"
                         f"Accounts posts_scraped Value -> {update_error}")


if __name__ == '__main__':
    account_data = {
        ('georgehotz', 54000): {'https://www.instagram.com/georgehotz/p/CQES8gwjcab/': [True, '', ''],
                                   'https://www.instagram.com/georgehotz/p/BOteX3HDcS2/': [True, '', ''],
                                   'https://www.instagram.com/georgehotz/p/Ci2vMapOo6L/': [True, '', ''],
                                   'https://www.instagram.com/georgehotz/p/CYo6WRTlHgK/': [True, '', ''],
                                   'https://www.instagram.com/georgehotz/p/Clwpf2cyY90/': [True, '', ''],}

    }
    UpdateDB().update(account_data)