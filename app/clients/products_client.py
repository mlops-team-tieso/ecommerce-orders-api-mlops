from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

import httpx


class ProductsClientError(Exception):
    """Generic error when communicating with the Products service."""


@dataclass
class Product:
    product_id: str
    name: str
    price: float
    stock: int
    available: Optional[bool] = None


def _get_products_base_url() -> str:
    base_url = os.getenv("PRODUCTS_SERVICE_URL")
    if not base_url:
        raise ProductsClientError(
            "PRODUCTS_SERVICE_URL environment variable is not set"
        )
    return base_url.rstrip("/")


class ProductsClient:
    """HTTP client for interacting with the Products microservice."""

    def __init__(self, client: Optional[httpx.Client] = None) -> None:
        self._client = client or httpx.Client(timeout=5.0)

    def get_product(self, product_id: str) -> Product:
        url = f"{_get_products_base_url()}/products/{product_id}"
        response = self._client.get(url)
        if response.status_code == 404:
            raise ProductsClientError("Product not found")
        response.raise_for_status()
        data = response.json()
        return Product(
            product_id=str(data["product_id"]),
            name=data["name"],
            price=float(data["price"]),
            stock=int(data["stock"]),
            available=data.get("available"),
        )

    def decrease_stock(self, product_id: str, quantity: int) -> None:
        if quantity <= 0:
            return
        # For simplicity we assume the Products service expects the final stock value.
        # In a real system this should be a dedicated 'decrease' endpoint.
        product = self.get_product(product_id)
        new_stock = product.stock - quantity
        if new_stock < 0:
            raise ProductsClientError("Resulting stock would be negative")

        url = f"{_get_products_base_url()}/products/{product_id}/stock"
        payload = {"stock": new_stock}
        response = self._client.put(url, json=payload)
        response.raise_for_status()
