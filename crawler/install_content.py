from typing import List, Optional, Dict, Union
from random import uniform
from abc import ABC, abstractmethod
import asyncio
import os

from bs4 import BeautifulSoup
import aiohttp

from utils.logger import get_logger
from config.config import ROOT_DIR

logger = get_logger("crawler_logger")


def update_data_paths(curr_post_data: Dict[str, List[Union[bool, str]]],
                             contents_data: Dict[str, str]) -> None:
    for content_url in contents_data:
        content_path = contents_data[content_url]
        curr_post_data[content_url][1] = content_path

    return None


class MediaDownload(ABC):
    def __init__(self, urls: List[str]):
        self.urls = urls
        self.account_name = self.urls[0].rstrip("/").split \
        ("/")[-3] if self.urls else ""

    def check_directory(self, img_directory: str) -> None:
        if not os.path.exists(img_directory):
            os.makedirs(img_directory)
        return None

    @abstractmethod
    def download(self):
        pass


class ImageDownload(MediaDownload):
    def __init__(self, urls: List[str]):
        super().__init__(urls)

    async def get_image_url(self, session: aiohttp.ClientSession,
                            post_url: str) -> Optional[str]:
        for _ in range(2):
            try:
                async with session.get(post_url, timeout=5) as response:
                    html_code = await response.text()
                    soup = BeautifulSoup(html_code, "html.parser")
                    meta_tag = soup.find('meta', property='og:image')
                    if meta_tag:
                        return meta_tag["content"]

            except Exception as e:
                logger.error(f"Image Request Error Occurred In {post_url} -> {e}")

        return None

    async def download_image_content(self, session: aiohttp.ClientSession,
                                     post_url: str) -> List[str]:
        try:
            unique_id = post_url.rstrip("/").split("/")[-1]
            image_url = await self.get_image_url(session, post_url)
            if not image_url:
                return [post_url, ""]

            img_directory = f"{ROOT_DIR}/data/{self.account_name}"
            self.check_directory(img_directory)
            img_path = f"{img_directory}/{unique_id}.jpg"

            async with session.get(image_url) as img_response:
                image_data = await img_response.read()
                with open(img_path, "wb") as file:
                    file.write(image_data)

            return [post_url, f"data/{self.account_name}/{unique_id}.jpg"]
        except Exception as image_error:
            logger.error(f"Error Occurred While Downloading "
                         f"Image -> {image_error}")
            return [post_url, ""]

    async def download(self, batch_size: int=60) -> Dict[str, str]:
        urls_length = len(self.urls)
        image_paths = {}
        async with aiohttp.ClientSession() as session:
            for i in range(0, urls_length, batch_size):
                curr_post_urls = self.urls[i:i + batch_size]
                tasks = [self.download_image_content(session, post_url)
                         for post_url in curr_post_urls]
                curr_image_paths = [c for c in await asyncio.gather(*tasks)]
                for curr in curr_image_paths:
                    image_paths[curr[0]] = curr[1]

                logger.info(f"Downloaded {i // batch_size + 1}. Image Batch!")
                await asyncio.sleep(uniform(3, 5))

        return image_paths


class VideoDownload(MediaDownload):
    def __init__(self, urls: List[str]):
        super().__init__(urls)

    async def download_video_content(self, post_url: str) -> List[str]:
        try:
            unique_id = post_url.rstrip("/").split("/")[-1]
            video_directory = f"{ROOT_DIR}/data/{self.account_name}"
            self.check_directory(video_directory)

            video_path = os.path.join(video_directory, f"{unique_id}.mp4")
            ytdlp_command = [
                "yt-dlp",
                "-f", "best",
                "-o", video_path,
                post_url
            ]

            process = await asyncio.create_subprocess_exec(
                *ytdlp_command,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )

            await process.communicate()
            if process.returncode == 0:
                return [post_url, f"data/{self.account_name}/{unique_id}.mp4"]
            else:
                raise Exception(f"Download failed for {post_url}")

        except Exception as video_error:
            logger.error(f"Error occurred while downloading video "
                         f"-> {video_error}")
            return [post_url, ""]


    async def download(self, batch_size: int=40) -> Dict[str, str]:
        video_paths = {}
        videos_length = len(self.urls)
        for i in range(0, videos_length, batch_size):
            curr_video_urls = self.urls[i:i + batch_size]
            tasks = [self.download_video_content(url)
                     for url in curr_video_urls]

            curr_video_paths = [v for v in await asyncio.gather(*tasks)]
            for curr in curr_video_paths:
                video_paths[curr[0]] = curr[1]

            logger.info(f"Downloaded {i // batch_size + 1}. Video Batch!")
            await asyncio.sleep(uniform(3, 15))

        return video_paths


if __name__ == '__main__':
    image_post_urls = [
        "https://www.instagram.com/georgehotz/p/C77Wl-OA_ue/",
        "https://www.instagram.com/georgehotz/p/Clwpf2cyY90/",
    ]

    video_post_urls = [
        "https://www.instagram.com/georgehotz/reel/DCrPAcmTRTU/",
    ]

    image_paths = asyncio.run(ImageDownload(image_post_urls).download())
    # video_paths = asyncio.run(VideoDownload(video_post_urls).download())
    print(image_paths)
    # print(video_paths)