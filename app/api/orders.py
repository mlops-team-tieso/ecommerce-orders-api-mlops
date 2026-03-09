from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.orders import (
    CreateOrderRequest,
    OrderResponse,
    UpdateOrderStatusRequest,
)
from app.services.orders_service import OrdersService, get_orders_service
from app.models.orders import OrderStatus


router = APIRouter()


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    payload: CreateOrderRequest,
    service: OrdersService = Depends(get_orders_service),
) -> OrderResponse:
    try:
        return service.create_order(payload)
    except ValueError as exc:
        # Used for domain-level validation like out-of-stock or invalid data
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: str,
    service: OrdersService = Depends(get_orders_service),
) -> OrderResponse:
    order = service.get_order(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order


@router.get(
    "",
    response_model=List[OrderResponse],
)
def list_orders(
    service: OrdersService = Depends(get_orders_service),
) -> List[OrderResponse]:
    return service.list_orders()


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def update_order_status(
    order_id: str,
    payload: UpdateOrderStatusRequest,
    service: OrdersService = Depends(get_orders_service),
) -> OrderResponse:
    try:
        new_status = OrderStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status",
        ) from exc

    order = service.update_order_status(order_id, new_status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order

