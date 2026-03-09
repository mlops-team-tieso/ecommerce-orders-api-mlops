from __future__ import annotations

from typing import List

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.orders import Order, OrderItem, OrderStatus
from app.schemas.orders import CreateOrderRequest, CreateOrderItemRequest
from app.services.orders_service import OrdersService


class InMemoryOrdersRepository:
    def __init__(self) -> None:
        self._orders = {}

    def create_order(self, order: Order) -> None:
        self._orders[order.order_id] = order

    def get_order(self, order_id: str):
        return self._orders.get(order_id)

    def list_orders(self) -> List[Order]:
        return list(self._orders.values())

    def update_order_status(self, order_id: str, new_status: OrderStatus):
        order = self._orders.get(order_id)
        if not order:
            return None
        order.status = new_status
        return order


class FakeProductsClient:
    def __init__(self) -> None:
        self.decrease_calls = []

    def get_product(self, product_id: int):
        # Always return a product with enough stock for tests
        from app.clients.products_client import Product

        return Product(
            product_id=product_id,
            name="Test Product",
            price=100.0,
            stock=10,
            available=True,
        )

    def decrease_stock(self, product_id: int, quantity: int) -> None:
        self.decrease_calls.append((product_id, quantity))


def get_test_service() -> OrdersService:
    repo = InMemoryOrdersRepository()
    products_client = FakeProductsClient()
    return OrdersService(repo, products_client)


@pytest.fixture
def client(monkeypatch):
    from app import services

    # Override dependency factory to use our in-memory implementations
    def _get_orders_service_override():
        return get_test_service()

    from app.services import orders_service as orders_service_module

    orders_service_module.get_orders_service = _get_orders_service_override

    test_client = TestClient(app)
    yield test_client


def test_create_order_success(client):
    payload = {
        "user_id": "user_1",
        "items": [{"product_id": 1, "quantity": 2}],
    }

    response = client.post("/orders", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "user_1"
    assert data["status"] == "PAID"
    assert data["total_price"] == 200.0
    assert len(data["items"]) == 1


def test_create_order_invalid_items(client):
    payload = {"user_id": "user_1", "items": []}
    response = client.post("/orders", json=payload)
    assert response.status_code == 422


def test_update_order_status_not_found(client):
    response = client.put("/orders/nonexistent/status", json={"status": "CANCELLED"})
    assert response.status_code == 404


def test_list_orders_empty(client):
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json() == []

