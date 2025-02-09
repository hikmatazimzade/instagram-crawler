import asyncio
from time import perf_counter
from typing import Optional, List, Dict, Union
from random import uniform

import aiohttp
from bs4 import BeautifulSoup

from utils.logger import get_logger

logger = get_logger("crawler_logger")


def update_data_descriptions(curr_post_data: Dict[str, List[Union[bool, str]]],
            descriptions_data: Dict[str, str]) -> None:
    for description_url in descriptions_data:
        description = descriptions_data[description_url]
        curr_post_data[description_url][2] = description


async def get_meta(session: aiohttp.ClientSession,
                   post_url: str) -> Optional[str]:
    for _ in range(2):
        try:
            async with session.get(post_url, timeout=5) as response:
                html_code = await response.text()
                soup = BeautifulSoup(html_code, "html.parser")
                meta_tag = soup.find('meta', property='og:description')
                if meta_tag:
                    return meta_tag["content"]

        except Exception as e:
            logger.error(f"Description Request Error Occurred In {post_url} -> {e}")

    return None


async def get_data(session: aiohttp.ClientSession,
                   post_url: str) -> List[str]:
    meta = await get_meta(session, post_url)
    if not meta or ":" not in meta:
        return [post_url, ""]
    col = meta.index(":") + 2

    description = meta[col:].rstrip(" ").rstrip(".")
    description = description.strip('"')
    return [post_url, description]


async def get_descriptions(post_urls: List[str], batch_size: int=60) ->(
        Optional)[Dict[str, str]]:
    posts_length = len(post_urls)
    descriptions = {}

    async with aiohttp.ClientSession() as session:
        for i in range(0, posts_length, batch_size):
            curr_post_urls = post_urls[i:i + batch_size]
            tasks = [get_data(session, post_url)
                     for post_url in curr_post_urls]
            curr_descriptions = [r for r in await asyncio.gather(*tasks)]
            for c in curr_descriptions:
                descriptions[c[0]] = c[1]

            logger.info(f"Fetched {i // batch_size + 1}. Description Batch!")
            await asyncio.sleep(uniform(3, 10))

    logger.info(f"{len(descriptions)} Post Descriptions Fetched!")
    return descriptions


if __name__ == "__main__":
    start_time = perf_counter()
    post_urls = [
        "https://www.instagram.com/georgehotz/reel/DCrPAcmTRTU/",
        "https://www.instagram.com/georgehotz/p/C77Wl-OA_ue/",
        "https://www.instagram.com/georgehotz/p/Clwpf2cyY90/",
    ]

    descriptions = asyncio.run(get_descriptions(post_urls))
    print(descriptions)
    # print(f"Execution Time for {len(descriptions)} posts ->", perf_counter() - start_time)