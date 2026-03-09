"""Products client - stub for CRUD-only; full HTTP implementation in integration commit."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class ProductsClientError(Exception):
    """Generic error when communicating with the Products service."""


@dataclass
class Product:
    product_id: int
    name: str
    price: float
    stock: int
    available: Optional[bool] = None


class ProductsClient:
    """Stub: HTTP integration with Products service added in integration commit."""

    def __init__(self, client=None) -> None:
        pass

    def get_product(self, product_id: int) -> Product:
        raise ProductsClientError("Products client not implemented (see integration commit)")

    def decrease_stock(self, product_id: int, quantity: int) -> None:
        raise ProductsClientError("Products client not implemented (see integration commit)")
