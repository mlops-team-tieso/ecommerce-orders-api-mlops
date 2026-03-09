from __future__ import annotations

import os
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Key

from app.models.orders import Order, OrderItem, OrderStatus


def _get_table_name() -> str:
    return os.getenv("ORDERS_TABLE_NAME", "orders")


def _get_region_name() -> str:
    return os.getenv("AWS_REGION", "us-east-2")


class OrdersRepository:
    """Repository that persists orders in a DynamoDB table."""

    def __init__(self, dynamodb_resource=None) -> None:
        if dynamodb_resource is None:
            dynamodb_resource = boto3.resource("dynamodb", region_name=_get_region_name())
        self._table = dynamodb_resource.Table(_get_table_name())

    def create_order(self, order: Order) -> None:
        self._table.put_item(Item=self._order_to_item(order))

    def get_order(self, order_id: str) -> Optional[Order]:
        response = self._table.get_item(Key={"order_id": order_id})
        item = response.get("Item")
        if not item:
            return None
        return self._item_to_order(item)

    def list_orders(self) -> List[Order]:
        # In a real system you might want to use queries with indexes;
        # for simplicity, we use scan here.
        response = self._table.scan()
        items = response.get("Items", [])
        return [self._item_to_order(it) for it in items]

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> Optional[Order]:
        response = self._table.update_item(
            Key={"order_id": order_id},
            UpdateExpression="SET #s = :s",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": new_status.value},
            ReturnValues="ALL_NEW",
        )
        attributes = response.get("Attributes")
        if not attributes:
            return None
        return self._item_to_order(attributes)

    @staticmethod
    def _order_to_item(order: Order) -> dict:
        return {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "status": order.status.value,
            "total_price": order.total_price,
            "created_at": order.created_at.isoformat(),
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "subtotal": item.subtotal,
                }
                for item in order.items
            ],
        }

    @staticmethod
    def _item_to_order(item: dict) -> Order:
        items = [
            OrderItem(
                product_id=int(it["product_id"]),
                name=it["name"],
                price=float(it["price"]),
                quantity=int(it["quantity"]),
                subtotal=float(it["subtotal"]),
            )
            for it in item.get("items", [])
        ]
        status = OrderStatus(item["status"])
        created_at_str = item.get("created_at")
        from datetime import datetime

        created_at = (
            datetime.fromisoformat(created_at_str)
            if created_at_str
            else datetime.utcnow()
        )
        return Order(
            order_id=item["order_id"],
            user_id=item["user_id"],
            status=status,
            total_price=float(item["total_price"]),
            items=items,
            created_at=created_at,
        )

