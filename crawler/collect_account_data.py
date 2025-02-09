from typing import List, Dict, Tuple
import os
import json
import asyncio
from random import uniform

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from utils.logger import get_logger
from config.config import ROOT_DIR

logger = get_logger("crawler_logger")


def get_cookies(cookies_path: str=ROOT_DIR/"cookies/cookies.json"):
    if not os.path.exists(cookies_path):
        raise ModuleNotFoundError("Cookies Not Found. First Run save_account_cookies.py script!")

    with open(cookies_path, "r") as json_file:
        cookies = json.load(json_file)
    return cookies


def turn_into_number(num_text: str) -> int:
    num_text = num_text.replace(",", "")
    num_dict = {
        "K": 3,
        "M": 6,
        "B": 9
    }
    for n in num_dict:
        if n in num_text:
            num_text = num_text.replace(n, "0" * num_dict[n])
            break

    return int(num_text)


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


class Parser:
    def __init__(self, content: str):
        self.soup = BeautifulSoup(content, "html.parser")

    def get_follower_meta(self):
        meta_tag = self.soup.find('meta', property='og:description')
        if meta_tag:
            return meta_tag["content"]
        return None

    def get_follower_number(self) -> int:
        try:
            follower_meta = self.get_follower_meta()
            if not follower_meta or " Followers" not in follower_meta:
                return 0

            followers_number = follower_meta[:follower_meta.index(" Followers")]
            return turn_into_number(followers_number)

        except Exception as follower_error:
            logger.error(f"Follower Error Occurred -> {follower_error}")
            return 0


    def get_post_ids(self, account_name: str):
        elements = self.soup.find_all(
            lambda tag: tag.has_attr("href") and (
                    tag["href"].startswith(f"/{account_name}/p/") or
                    tag["href"].startswith(f"/{account_name}/reel/")
            )
        )
        return [element["href"] for element in elements]


class Page:
    def __init__(self, url: str, context: async_playwright):
        self.url = url
        self.context = context
        self.post_urls = []

    async def navigate_url(self, max_try: int=2) -> None:
        self.page = await self.context.new_page()

        for _ in range(max_try):
            try:
                await self.page.goto(self.url, wait_until="networkidle")
                break

            except Exception as navigate_error:
                logger.error("Account Data Scraping Navigation Error -> "
                             f"{self.url} {navigate_error}")
                await asyncio.sleep(uniform(2, 3))

    async def get_current_ids(self, account_name: str) -> List[str]:
        content = await self.get_content()
        parser = Parser(content)
        current_ids = parser.get_post_ids(account_name)

        await self.scroll()
        return current_ids

    async def fetch_account_data(self, account_name: str,
                            max_scrolls: int=100) -> Tuple[List[str], int]:
        await self.navigate_url()
        content = await self.get_content()
        follower_number = Parser(content).get_follower_number()

        post_ids = set()
        for _ in range(max_scrolls):
            new = False
            current_ids = await self.get_current_ids(account_name)
            for current_id in current_ids:
                if current_id not in post_ids:
                    post_ids.add(current_id)
                    new = True

            if not new:
                break

        return ([f"https://www.instagram.com{post_id}" for post_id in post_ids], follower_number)

    async def scroll(self) -> None:
        await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(uniform(3, 5))

    async def get_content(self) -> str:
        content = await self.page.content()
        return content


def get_urls_dict(account_data: List[Tuple[List, int]])\
        -> Dict[Tuple[str, int], Dict[str, List]]:
    urls_dict = {}
    for curr_data in account_data:
        if curr_data[0]:
            post_urls, follower_number = curr_data
            account_name = post_urls[0].rstrip("/").split("/")[-3]
            full_data = {}
            for url in post_urls:
                post_type = True if url.rstrip("/").split("/")[-2] == "p" else False
                full_data[url] = (
                    [post_type, "", ""]
                )

            urls_dict[(account_name, follower_number)] = full_data
            # [{(post_url, follower): [type, download_path, description], ....]

    return urls_dict


async def get_accounts_data(accounts_urls: List[str])\
        -> Dict[Tuple[str, int], Dict[str, List]]:
    logger.info(f"Scraping Accounts Post Urls...")
    account_data, accounts_length = [], len(accounts_urls)
    for chunk_num in range(0, accounts_length, 10):
        chunk_account_urls = accounts_urls[chunk_num:chunk_num + 10]

        async with async_playwright() as pl:
            chromium = Chromium(pl)
            await chromium.initialize()

            tasks = [Page(url, chromium.context).fetch_account_data
                (url.strip("/").split("/")[-1]) for url in chunk_account_urls]
            chunk_accounts_data = await asyncio.gather(*tasks)
            account_data.extend(chunk_accounts_data)

            await chromium.close()
            await asyncio.sleep(uniform(10, 15))

    urls_dict = get_urls_dict(account_data)
    return urls_dict


if __name__ == '__main__':
    accounts_urls = [
        "https://www.instagram.com/georgehotz/",
    ]
    account_data = asyncio.run(get_accounts_data(accounts_urls))
    print(account_data)
    for url in account_data:
        print(f"{url} => {account_data[url]}")