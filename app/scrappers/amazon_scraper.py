import httpx
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.google.com/"
}


async def fetch_html(url: str):

    async with httpx.AsyncClient(
        follow_redirects=True
    ) as client:

        response = await client.get(
            url,
            headers=HEADERS,
            timeout=30
        )

    return BeautifulSoup(response.text, "lxml")


async def scrape_amazon_product(url: str):
     
    soup = await fetch_html(url)

    title = None
    price = None

    title_tag = soup.select_one("#productTitle")

    if title_tag:
        title = title_tag.get_text(strip=True)

        price_tag = soup.select_one("span.a-offscreen")

        if price_tag:
            price = price_tag.get_text(strip=True)

        return {
            "platform": "amazon",
            "title": title,
            "price": price
        }

 
async def scrape_flipkart_product(url: str):

    soup = await fetch_html(url)

    title = None
    price = None

    # title
    title_tag = (
        soup.select_one("span.VU-ZEz") or
        soup.select_one("span.B_NuCI")
    )

    if title_tag:
        title = title_tag.get_text(strip=True)

    # price
    price_tag = (
        soup.select_one("div.Nx9bqj") or
        soup.select_one("div._30jeq3")
    )

    if price_tag:
        price = price_tag.get_text(strip=True)

    return {
        "platform": "flipkart",
        "title": title,
        "price": price,
        "product_url": url
    }


 

async def scrape_meesho_product(url: str):

    soup = await fetch_html(url)

    title = None
    price = None

    title_tag = (
        soup.select_one("h1") or
        soup.select_one("[data-testid='product-title']")
    )

    if title_tag:
        title = title_tag.get_text(strip=True)

    price_tag = (
        soup.select_one("h4") or
        soup.select_one("[data-testid='product-price']")
    )

    if price_tag:
        price = price_tag.get_text(strip=True)

    return {
        "platform": "meesho",
        "title": title,
        "price": price,
        "product_url": url
    }


 

async def scrape_myntra_product(url: str):

    soup = await fetch_html(url)

    title = None
    price = None

    brand_tag = soup.select_one("h1.pdp-title")
    product_tag = soup.select_one("h1.pdp-name")

    if brand_tag and product_tag:
        title = (
            f"{brand_tag.get_text(strip=True)} "
            f"{product_tag.get_text(strip=True)}"
        )

    price_tag = soup.select_one("span.pdp-price strong")

    if price_tag:
        price = price_tag.get_text(strip=True)

    return {
        "platform": "myntra",
        "title": title,
        "price": price,
        "product_url": url
    }


 

async def scrape_alibaba_product(url: str):

    soup = await fetch_html(url)

    title = None
    price = None

    title_tag = (
        soup.select_one("h1") or
        soup.select_one(".title-text")
    )

    if title_tag:
        title = title_tag.get_text(strip=True)

    price_tag = (
        soup.select_one(".price") or
        soup.select_one(".price-range")
    )

    if price_tag:
        price = price_tag.get_text(strip=True)

    return {
        "platform": "alibaba",
        "title": title,
        "price": price,
        "product_url": url
    }


# import httpx
# from bs4 import BeautifulSoup

# async def scrape_amazon_product(url: str):

#     headers = {
#         "User-Agent": (
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/124.0.0.0 Safari/537.36"
#         ),
#         "Accept-Language": "en-US,en;q=0.9",
#         "Accept": "text/html,application/xhtml+xml",
#         "Referer": "https://www.google.com/"
#     }

#     async with httpx.AsyncClient(follow_redirects=True) as client:

#         response = await client.get(
#             url,
#             headers=headers,
#             timeout=30
#         )

#     print(response.status_code)

#     soup = BeautifulSoup(response.text, "lxml")

#     title = None
#     price = None

#     title_tag = soup.select_one("#productTitle")

#     if title_tag:
#         title = title_tag.get_text(strip=True)

#     price_tag = soup.select_one("span.a-offscreen")

#     if price_tag:
#         price = price_tag.get_text(strip=True)

#     return {
#         "platform": "amazon",
#         "title": title,
#         "price": price
#     }



# import httpx
# from bs4 import BeautifulSoup

# async def scrape_amazon_product(url: str):

#     headers = {
#         "User-Agent": (
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#         )
#     }

#     async with httpx.AsyncClient() as client:

#         response = await client.get(
#             url,
#             headers=headers,
#             timeout=20
#         )

#     soup = BeautifulSoup(response.text, "lxml")

#     title = None
#     price = None

#     title_tag = soup.select_one("#productTitle")

#     if title_tag:
#         title = title_tag.text.strip()

#     price_tag = soup.select_one(".a-price-whole")

#     if price_tag:
#         price = price_tag.text.strip()

#     return {
#         "platform": "amazon",
#         "title": title,
#         "price": price,
#         "product_url": url
#     }