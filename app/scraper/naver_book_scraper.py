import os
from typing import List, Dict

import asyncio
import aiohttp

from dotenv import load_dotenv

load_dotenv()


class NaverBookScraper:
    NAVER_API_BOOK = "https://openapi.naver.com/v1/search/book"
    NAVER_API_ID = os.environ.get("NAVER_API_ID")
    NAVER_API_SECRET = os.environ.get("NAVER_API_SECRET")

    @staticmethod
    async def fetch(session, url, headers):
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                res = await response.json()
                return res["items"]

    def unit_url(self, keyword, start):
        return {
            "url": f"{self.NAVER_API_BOOK}?query={keyword}&display=10&start={start}",
            "headers": {
                "X-Naver-Client-Id": self.NAVER_API_ID,
                "X-Naver-Client-Secret": self.NAVER_API_SECRET,
            },
        }

    async def search(self, keyword, total_page):
        apis = [self.unit_url(keyword, 1 + i * 10) for i in range(total_page)]
        async with aiohttp.ClientSession() as session:
            all_data = await asyncio.gather(
                *[self.fetch(session, api["url"], api["headers"]) for api in apis]
            )

            res: List = []

            for data in all_data:
                if data:
                    res.extend(data)

            return res

    def run(self, keyword, total_page):
        return asyncio.run(self.search(keyword, total_page))


if __name__ == "__main__":
    scraper = NaverBookScraper()
    results = scraper.run("파이썬", 10)
    print(results)
    print(len(results))
