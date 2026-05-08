# //here we decalre the schemas for product query

from pydantic import BaseModel
from typing import List, Optional , Dict , Any


class ProductUnderstanding(BaseModel):
    brand: Optional[str] = None
    product_name: Optional[str] = None
    model: Optional[str] = None

    category: Optional[str] = None
    subcategory: Optional[str] = None

    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    storage: Optional[str] = None
    weight: Optional[str] = None
    gender: Optional[str] = None

    specifications: Dict[str, Any] = {}

    keywords: List[str] = []




class ProductRequest(BaseModel):
    product_name: str
    product_link: str