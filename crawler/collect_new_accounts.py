from typing import List
import os
import json
import asyncio
from random import uniform

from playwright.async_api import async_playwright

from utils.logger import get_logger
from config.config import ROOT_DIR

logger = get_logger("crawler_logger")


def get_cookies(cookies_path: str=ROOT_DIR/"cookies/cookies.json"):
    if not os.path.exists(cookies_path):
        raise ModuleNotFoundError(
            "Cookies Not Found. First Run save_account_cookies.py script!")

    with open(cookies_path, "r") as json_file:
        cookies = json.load(json_file)
    return cookies


class CollectFollowing:
    def __init__(self, context: async_playwright, url: str):
        self.context = context
        self.url = url
        self.following_accounts = []

    async def navigate_url(self, max_try: int=2) -> None:
        self.page = await self.context.new_page()

        for _ in range(max_try):
            try:
                await self.page.goto(self.url, wait_until="networkidle")
                break

            except Exception as navigate_error:
                logger.error(f"Account Crawling Navigation Error -> "
                             f"{self.url} {navigate_error}")
                await asyncio.sleep(uniform(2, 3))

    async def fetch_following_accounts(self,
            account_name: str, max_scrolls: int=100) -> List[str]:
        await self.navigate_url()
        await self.page.click(f'a[href="/{account_name}/following/"]')
        await asyncio.sleep(uniform(5, 7))


        profiles_length, profiles = 0, []
        for _ in range(max_scrolls):
            img_elements = await (self.page.query_selector_all
                            ("img[alt$='s profile picture']"))
            profiles = [await i.get_attribute("alt") for i in
                        img_elements[2:]]
            profiles = [p.replace("'s profile picture", "")
                        for p in profiles if p]

            if len(profiles) == profiles_length:
                break

            profiles_length = len(profiles)
            for _ in range(2):
                try:
                    await img_elements[-1].scroll_into_view_if_needed()
                    await asyncio.sleep(uniform(3, 5))

                except Exception as scroll_error:
                    logger.error("Error Occurred While Scrolling In "
                        f"Following Accounts Collecting -> {scroll_error}")

        profiles = [f"https://www.instagram.com/{profile}" for
                    profile in profiles]
        logger.info(f"Fetched {profiles_length} accounts from {account_name}")
        return profiles


class Chromium:
    def __init__(self, pl):
        self.pl = pl

    async def load_cookies(self):
        cookies = get_cookies()
        await self.context.add_cookies(cookies)

    async def initialize(self):
        self.browser = await self.pl.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        await self.load_cookies()

    async def close(self):
        await self.browser.close()


async def get_following_accounts(account_url: str) -> List[str]:
    account_name = account_url.rstrip("/").split("/")[-1]
    logger.info(f"Collecting Following Account Urls From {account_url}")
    following_accounts = []
    try:
        async with async_playwright() as pl:
            chromium = Chromium(pl)
            await chromium.initialize()

            following_accounts = await CollectFollowing(chromium.context,
                        account_url).fetch_following_accounts(account_name)
            await chromium.close()
            if following_accounts:
                await asyncio.sleep(uniform(10, 15))

        return following_accounts

    except Exception as following_error:
        logger.error(f"An Error Occurred While Fetching "
            f"Following Accounts From {account_name} -> {following_error}")
        return following_accounts


if __name__ == '__main__':
    following_accounts = (
        asyncio.run(get_following_accounts(
            "https://www.instagram.com/cristiano/"
        )))
    print(following_accounts)