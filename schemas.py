"""
Database Schemas for Sunny Online Store

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.

Use these schemas for validation when creating documents through API endpoints.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl, EmailStr

class Product(BaseModel):
    """
    Collection: product
    """
    name: str = Field(..., description="Product name")
    price: float = Field(..., ge=0, description="Price in USD")
    image: HttpUrl = Field(..., description="Image URL")
    badge: Optional[str] = Field(None, description="Optional badge like 'Bestseller'")
    rating: float = Field(4.7, ge=0, le=5, description="Average rating 0-5")
    category: Optional[str] = Field(None, description="Product category")
    in_stock: bool = Field(True, description="Availability flag")

class OrderItem(BaseModel):
    product_id: Optional[str] = Field(None, description="Referenced product id as string")
    name: str
    price: float
    qty: int = Field(1, ge=1)
    image: Optional[HttpUrl] = None

class Order(BaseModel):
    """
    Collection: order
    """
    items: List[OrderItem]
    total: float = Field(..., ge=0)
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    customer_address: Optional[str] = None
    status: str = Field("pending", description="Order status: pending, paid, shipped, completed, cancelled")

class AdminLogin(BaseModel):
    password: str
