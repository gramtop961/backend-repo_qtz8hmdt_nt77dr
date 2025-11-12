"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional

# Example schemas (you can keep these for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# App-specific schemas

class Car(BaseModel):
    """
    Cars collection schema
    Collection name: "car"
    """
    brand: str = Field(..., description="Car brand/manufacturer")
    model: str = Field(..., description="Car model name")
    year: int = Field(..., ge=1990, le=2100, description="Model year")
    price: float = Field(..., ge=0, description="Price in USD")
    horsepower: int = Field(..., ge=30, le=2000, description="Engine horsepower")
    mpg: float = Field(..., ge=5, le=200, description="Fuel economy (combined MPG)")
    safety_rating: float = Field(..., ge=0, le=5, description="Safety rating out of 5")
    seating: int = Field(..., ge=1, le=9, description="Number of seats")
    drivetrain: str = Field(..., description="FWD / RWD / AWD / 4WD")
    body_type: str = Field(..., description="Sedan, SUV, Truck, Coupe, Hatchback, etc.")
