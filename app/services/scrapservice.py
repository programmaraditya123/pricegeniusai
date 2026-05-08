import asyncio

from app.scrappers.amazon_scraper import scrape_amazon_product

async def scrape_products(search_results):

    tasks = []

    for platform, products in search_results.items():

        # AMAZON
        if platform == "amazon":

            for item in products:

                tasks.append(
                    scrape_amazon_product(
                        item["link"]
                    )
                )

    results = await asyncio.gather(*tasks)

    return results