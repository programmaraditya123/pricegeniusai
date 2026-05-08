import asyncio
from typing import List, Dict, Any

from langchain_community.utilities import GoogleSerperAPIWrapper
from dotenv import load_dotenv

load_dotenv()
 

search = GoogleSerperAPIWrapper()


async def search_platform(
    platform: str,
    product_query: str,
    limit: int = 5
) -> List[Dict[str, Any]]:

    google_query = f"site:{platform} {product_query}"

    try:

        result = await asyncio.to_thread(
            search.results,
            google_query
        )

        organic_results = result.get("organic", [])

        products = []

        for item in organic_results[:limit]:

            products.append({
                "platform": platform,
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet"),
            })

        return products

    except Exception as e:

        print(f"{platform} search error:", e)

        return []


async def search_flipkart(product_query: str):

    return await search_platform(
        "flipkart.com",
        product_query
    )


async def search_amazon(product_query: str):

    return await search_platform(
        "amazon.in",
        product_query
    )


async def search_myntra(product_query: str):

    return await search_platform(
        "myntra.com",
        product_query
    )


async def search_alibaba(product_query: str):

    return await search_platform(
        "alibaba.com",
        product_query
    )


async def search_meesho(product_query: str):

    return await search_platform(
        "meesho.com",
        product_query
    )


async def search_all_platforms(product_query: str):

    tasks = [

        search_flipkart(product_query),

        search_amazon(product_query),

        search_myntra(product_query),

        search_alibaba(product_query),

        search_meesho(product_query),
    ]

    results = await asyncio.gather(*tasks)

    return {
        "flipkart": results[0],
        "amazon": results[1],
        "myntra": results[2],
        "alibaba": results[3],
        "meesho": results[4],
    }


async def main():

    query = "Apple iPhone 15 128GB"

    results = await search_all_platforms(query)

    print(results)

# -----------------------------------

if __name__ == "__main__":

    asyncio.run(main())