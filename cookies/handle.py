import os
import json

from utils.logger import get_logger
from config.config import ROOT_DIR
from cookies.save_account_cookies import login

logger = get_logger("cookies_logger")


def check_cookies_json() -> bool:
    return os.path.exists(f"{ROOT_DIR}/cookies/cookies.json")

def check_login() -> bool:
    with open(f"{ROOT_DIR}/cookies/cookies.json", "r", encoding="utf-8") \
        as cookies_file:
        try:
            cookies_data = json.load(cookies_file)
        except Exception as cookies_error:
            logger.error(f"Cookies aren't in right format! -> "
                         f"{cookies_error}")
            return False

    for cookies in cookies_data:
        if isinstance(cookies, dict) and cookies.get("name") == "ds_user_id":
            return True

    logger.warning(f"Cookies expired or couldn't login account!")
    return False

async def handle_cookies() -> bool:
    if check_cookies_json():
        logger.info("Account cookies exist!")
        return True

    else:
        logger.info("Account cookies missing, logging account")
        login_result = await login()
        return login_result



if __name__ == '__main__':
    import asyncio
    print(asyncio.run(handle_cookies()))
    print(check_login())