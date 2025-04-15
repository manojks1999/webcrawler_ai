from pydantic import BaseModel
from typing import Optional


class Product(BaseModel):
    url: str
    domain: str 
    product_id: Optional[str] = None
    category: Optional[str] = None