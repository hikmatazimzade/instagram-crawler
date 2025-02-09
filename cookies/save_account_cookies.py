from typing import Tuple
from random import uniform
from time import sleep
import os
import json

from playwright.async_api import async_playwright
from dotenv import load_dotenv

from config.config import ROOT_DIR
from utils.logger import get_logger

logger = get_logger("cookies_logger")


class Env:
    def __init__(self, env_path: str=f"{ROOT_DIR}/cookies/.account_env"):
        load_dotenv(env_path)

    def get_data(self) -> Tuple[str, str]:
        email = os.getenv("email")
        password = os.getenv("password")
        return email, password


class Chromium:
    def __init__(self, pl: async_playwright):
        self.pl = pl

    async def initialize(self):
        self.browser = await self.pl.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def save_cookies(self, file_path:
    str=f"{ROOT_DIR}/cookies/cookies.json") -> None:
        cookies = await self.context.cookies()
        with open(file_path, "w") as cookies_file:
            json.dump(cookies, cookies_file) # type: ignore
        logger.info(f"Saved cookies into {file_path}!")


class Instagram:
    def __init__(self, page: async_playwright):
        self.page = page
        data = Env().get_data()
        self.email, self.password = data

    async def navigate_to_instagram(self) -> None:
        try:
            await self.page.goto("https://www.instagram.com", wait_until="networkidle")
            logger.info("Instagram opened!")
            await self.page.wait_for_selector('[aria-label="Password"]')

        except Exception as e:
            raise ValueError("Failed to load instagram")

    async def input_data(self) -> None:
        await self.page.locator('[aria-label="Phone number, username, or email"]').fill(self.email)
        await self.page.locator('[aria-label="Password"]').fill(self.password)
        await self.page.locator('[aria-label="Password"]').press("Enter")
        logger.info("Logging into account...")


async def handle_instagram(instagram: Instagram) -> None:
    await instagram.navigate_to_instagram()
    await instagram.input_data()
    sleep(uniform(7, 10))


async def login() -> bool:
    async with async_playwright() as pl:
        chromium = Chromium(pl)
        await chromium.initialize()

        instagram = Instagram(chromium.page)
        if not instagram.email or not instagram.password:
            logger.warning(f"Input email and password in .account_env file!")
            return False

        await handle_instagram(instagram)

        await chromium.save_cookies()
        await chromium.browser.close()

    return True


if __name__ == '__main__':
    import asyncio
    asyncio.run(login())