import asyncio

from app.scrappers.amazon_scraper import scrape_amazon_product
from app.scrappers.amazon_scraper import scrape_flipkart_product
from app.scrappers.amazon_scraper import scrape_meesho_product
from app.scrappers.amazon_scraper import scrape_myntra_product
from app.scrappers.amazon_scraper import scrape_alibaba_product


async def scrape_products(search_results):

    tasks = []

    for platform, products in search_results.items():

      
        if platform == "amazon":

            for item in products:

                tasks.append(
                    scrape_amazon_product(
                        item["link"]
                    )
                )

      
        elif platform == "flipkart":

            for item in products:

                tasks.append(
                    scrape_flipkart_product(
                        item["link"]
                    )
                )

        
        elif platform == "meesho":

            for item in products:

                tasks.append(
                    scrape_meesho_product(
                        item["link"]
                    )
                )

        elif platform == "myntra":

            for item in products:

                tasks.append(
                    scrape_myntra_product(
                        item["link"]
                    )
                )

     
        elif platform == "alibaba":

            for item in products:

                tasks.append(
                    scrape_alibaba_product(
                        item["link"]
                    )
                )

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    final_results = []

    for result in results:

        if isinstance(result, Exception):

            print("Scraping Error:", result)

            continue

        final_results.append(result)

    return final_results

# import asyncio

# from app.scrappers.amazon_scraper import scrape_amazon_product

# async def scrape_products(search_results):

#     tasks = []

#     for platform, products in search_results.items():

#         # AMAZON
#         if platform == "amazon":

#             for item in products:

#                 tasks.append(
#                     scrape_amazon_product(
#                         item["link"]
#                     )
#                 )

#     results = await asyncio.gather(*tasks)

#     return results