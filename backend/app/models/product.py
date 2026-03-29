from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class ProductCategory(str, Enum):
    SHIRT = "shirt"
    DRESS = "dress"
    JACKET = "jacket"
    PANTS = "pants"
    SAREE = "saree"
    KURTA = "kurta"


class Product(BaseModel):
    id: str
    name: str
    category: ProductCategory
    description: str
    price: float
    image_url: str
    sizes: List[str] = ["S", "M", "L", "XL"]
    colors: List[str] = ["Black", "White"]


class TryOnRequest(BaseModel):
    product_id: str
    person_image: str  # base64 or file path
    custom_prompt: Optional[str] = None


class TryOnJob(BaseModel):
    job_id: str
    product_id: str
    status: str  # "pending", "processing", "completed", "failed"
    result_image_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: float
    completed_at: Optional[float] = None
