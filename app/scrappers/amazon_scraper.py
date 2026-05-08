import httpx
from bs4 import BeautifulSoup

async def scrape_amazon_product(url: str):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            url,
            headers=headers,
            timeout=20
        )

    soup = BeautifulSoup(response.text, "lxml")

    title = None
    price = None

    title_tag = soup.select_one("#productTitle")

    if title_tag:
        title = title_tag.text.strip()

    price_tag = soup.select_one(".a-price-whole")

    if price_tag:
        price = price_tag.text.strip()

    return {
        "platform": "amazon",
        "title": title,
        "price": price,
        "product_url": url
    }