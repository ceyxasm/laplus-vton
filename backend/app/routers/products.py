from fastapi import APIRouter, HTTPException
from typing import List
import json
import os

from app.models.product import Product

router = APIRouter(prefix="/api/products", tags=["products"])

# Load products from JSON
PRODUCTS_FILE = os.path.join(os.path.dirname(__file__), "../../data/products.json")


def load_products() -> List[Product]:
    try:
        with open(PRODUCTS_FILE, "r") as f:
            data = json.load(f)
            return [Product(**item) for item in data]
    except Exception as e:
        print(f"Error loading products: {e}")
        return []


@router.get("", response_model=List[Product])
async def get_products(category: str = None):
    """Get all products or filter by category"""
    products = load_products()

    if category:
        products = [p for p in products if p.category == category]

    return products


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a single product by ID"""
    products = load_products()

    product = next((p for p in products if p.id == product_id), None)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product
