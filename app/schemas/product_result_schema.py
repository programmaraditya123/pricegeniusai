from pydantic import BaseModel
from typing import Optional

class ProductResult(BaseModel):

    platform: str

    title: Optional[str] = None

    price: Optional[float] = None

    currency: Optional[str] = None

    rating: Optional[float] = None

    reviews_count: Optional[int] = None

    seller: Optional[str] = None

    discount_percentage: Optional[float] = None

    availability: Optional[bool] = None

    image_url: Optional[str] = None

    product_url: Optional[str] = None