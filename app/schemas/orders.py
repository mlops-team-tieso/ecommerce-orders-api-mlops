from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, validator


class CreateOrderItemRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)


class CreateOrderRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    items: List[CreateOrderItemRequest]

    @validator("items")
    def validate_items(
        cls, value: List[CreateOrderItemRequest]
    ) -> List[CreateOrderItemRequest]:
        if not value:
            raise ValueError("Order must contain at least one item")
        return value


class OrderItemSchema(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int
    subtotal: float


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    status: str
    total_price: float
    items: List[OrderItemSchema]
    created_at: datetime

    class Config:
        orm_mode = True


class UpdateOrderStatusRequest(BaseModel):
    status: str
