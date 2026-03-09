from __future__ import annotations

import uuid
from typing import List, Optional

from app.clients.products_client import ProductsClient, ProductsClientError
from app.models.orders import Order, OrderItem, OrderStatus
from app.repositories.orders_repository import OrdersRepository
from app.schemas.orders import CreateOrderRequest, OrderResponse


class OrdersService:
    """Business logic for handling orders."""

    def __init__(
        self,
        repository: OrdersRepository,
        products_client: ProductsClient,
    ) -> None:
        self._repository = repository
        self._products_client = products_client

    def create_order(self, payload: CreateOrderRequest) -> OrderResponse:
        if not payload.items:
            raise ValueError("Order must contain at least one item")

        items: List[OrderItem] = []
        total_price = 0.0

        # Validate stock and enrich items with product data
        for item_req in payload.items:
            try:
                product = self._products_client.get_product(item_req.product_id)
            except ProductsClientError as exc:
                raise ValueError(str(exc)) from exc

            if product.available is False:
                raise ValueError(f"Product {product.product_id} is not available")

            if item_req.quantity > product.stock:
                raise ValueError(f"Product {product.product_id} out of stock")

            subtotal = product.price * item_req.quantity
            total_price += subtotal
            items.append(
                OrderItem(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    quantity=item_req.quantity,
                    subtotal=subtotal,
                )
            )

        # Simulate payment processing (could be expanded if needed)
        self._simulate_payment(total_price)

        # Decrease stock in Products service
        for order_item in items:
            try:
                self._products_client.decrease_stock(
                    product_id=order_item.product_id,
                    quantity=order_item.quantity,
                )
            except ProductsClientError as exc:
                # In a real system we would implement compensation logic.
                raise ValueError(str(exc)) from exc

        order = Order(
            order_id=_generate_order_id(),
            user_id=payload.user_id,
            status=OrderStatus.PAID,
            total_price=total_price,
            items=items,
        )

        self._repository.create_order(order)
        return self._to_response(order)

    def get_order(self, order_id: str) -> Optional[OrderResponse]:
        order = self._repository.get_order(order_id)
        if not order:
            return None
        return self._to_response(order)

    def list_orders(self) -> List[OrderResponse]:
        orders = self._repository.list_orders()
        return [self._to_response(order) for order in orders]

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> Optional[OrderResponse]:
        order = self._repository.update_order_status(order_id, new_status)
        if not order:
            return None
        return self._to_response(order)

    @staticmethod
    def _to_response(order: Order) -> OrderResponse:
        return OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            status=order.status.value,
            total_price=order.total_price,
            created_at=order.created_at,
            items=[
                {
                    "product_id": item.product_id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal,
                }
                for item in order.items
            ],
        )

    @staticmethod
    def _simulate_payment(amount: float) -> None:
        # For this project we just simulate success.
        if amount <= 0:
            raise ValueError("Total amount must be greater than zero to process payment")


def _generate_order_id() -> str:
    return f"order_{uuid.uuid4().hex[:12]}"


def get_orders_service() -> OrdersService:
    """FastAPI dependency factory for OrdersService."""
    repository = OrdersRepository()
    products_client = ProductsClient()
    return OrdersService(repository, products_client)

