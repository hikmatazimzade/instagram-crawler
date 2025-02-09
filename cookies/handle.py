import os

from utils.logger import get_logger
from config.config import ROOT_DIR
from cookies.save_account_cookies import login

logger = get_logger("cookies_logger")


def check_cookies_json() -> bool:
    return os.path.exists(f"{ROOT_DIR}/cookies/cookies.json")


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