from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


@dataclass
class OrderItem:
    product_id: str
    name: str
    price: float
    quantity: int
    subtotal: float


@dataclass
class Order:
    order_id: str
    user_id: str
    status: OrderStatus
    total_price: float
    items: List[OrderItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
