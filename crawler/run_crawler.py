import asyncio
from typing import List, Dict, Tuple, Union
from random import uniform

from crawler.collect_account_data import get_accounts_data
from crawler.collect_new_accounts import get_following_accounts
from crawler.collect_post_descriptions import get_descriptions, update_data_descriptions
from crawler.install_content import VideoDownload, ImageDownload, update_data_paths
from db.handle_followers import FollowerDB
from db.create_table import CreateDB
from db.write_data import WriteDB
from db.update_posts import UpdateDB
from cookies.handle import handle_cookies, check_login
from utils.logger import get_logger

logger = get_logger("crawler_logger")


def get_split_posts(curr_post_data: Dict[str, List[Union[bool, str]]]) -> (
        Tuple)[List[str], List[str]]:
    image_posts, video_posts = [], []
    for c in curr_post_data:
        if curr_post_data[c][0]:
            image_posts.append(c)
        else:
            video_posts.append(c)

    return image_posts, video_posts


def update_data(curr_posts_data, descriptions_data=None, images_data=None,
            videos_data=None) -> None:
    if descriptions_data:
        update_data_descriptions(curr_posts_data, descriptions_data)
    if images_data:
        update_data_paths(curr_posts_data, images_data)
    if videos_data:
        update_data_paths(curr_posts_data, videos_data)


async def get_data(account_urls: List[str]) -> (
        Dict)[Tuple[str, int], Dict[str, List]]:
    account_data = await get_accounts_data(account_urls)
    logger.info(f"Scraping Account Details... -> {account_urls}")

    for account_detail in account_data:
        curr_posts_data = account_data[account_detail]
        if curr_posts_data:
            post_urls = [c for c in curr_posts_data]
            descriptions_data = await get_descriptions(post_urls)
            image_posts, video_posts = get_split_posts(curr_posts_data)

            images_data = await ImageDownload(image_posts).download()\
                if image_posts else None
            # videos_data = await VideoDownload(video_posts).download()\
            #     if video_posts else None
            update_data(curr_posts_data, descriptions_data, images_data)

    random_time = uniform(60, 120)
    logger.info(f"Sleeping For {int(random_time)} Seconds...")
    await asyncio.sleep(random_time)
    return account_data


async def run(accounts_urls: List[str]) -> None:
    cookies_state = await handle_cookies()
    login_state = check_login()

    if not cookies_state or not login_state:
        return

    CreateDB().create()
    logger.info("Crawler Started Working...")
    while True:
        logger.info(f"Account Urls -> {accounts_urls}")
        try:
            account_data = await get_data(accounts_urls)
            WriteDB().write(account_data)
            UpdateDB().update(account_data)

            most_follower_user_url = FollowerDB().get_most_follower_user()
            accounts_urls = await get_following_accounts(most_follower_user_url)
            await asyncio.sleep(uniform(30, 60))

        except Exception as run_error:
            logger.error(f"Main Loop Error -> {run_error}")