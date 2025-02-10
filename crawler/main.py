import asyncio

from crawler.run_crawler import run


if __name__ == '__main__':
    initial_urls = [
        "https://www.instagram.com/georgehotz/",
        "https://www.instagram.com/openai/",
        "https://www.instagram.com/tech_with_tim/",
    ]
    asyncio.run(run(initial_urls))