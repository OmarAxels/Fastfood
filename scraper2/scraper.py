import asyncio
from crawl4ai import *

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.kfc.is/menu",
        )
        print(result.markdown)
        with open("kfc_menu.md", "w", encoding="utf-8") as f:
            f.write(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())