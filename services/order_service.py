from typing import List, Optional
import asyncio
from models.order import Order, OrderStatus
from app.exceptions import OrderNotFoundError, InvalidOrderStatusError
import uuid
from datetime import datetime

class OrderService:
    def __init__(self):
        self.orders: List[Order] = []
        self._lock = None

    async def _ensure_lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()

    async def create_order(self, order_data: dict) -> Order:
        print("#### Before adding order, orders list:", self.orders)
        await self._ensure_lock()

        order = Order(
            id=str(uuid.uuid4().int)[:5],
            **order_data,
            timestamp=datetime.now()
        )

        async with self._lock:
            self.orders.append(order)
            print("#### After adding order, orders list:", self.orders)
        return order

    async def get_orders(self) -> List[Order]:
        return self.orders

    async def update_order_status(self, order_id: str, status: str) -> Order:
        await self._ensure_lock()

        try:
            new_status = OrderStatus(status)
        except ValueError:
            raise InvalidOrderStatusError()

        async with self._lock:
            for order in self.orders:
                if order.id == order_id:
                    order.status = new_status
                    return order

        raise OrderNotFoundError()

    async def get_order(self, order_id: str) -> Optional[Order]:
        return next((order for order in self.orders if order.id == order_id), None)


_order_service_instance = None

def get_order_service():
    # Ensure we are only creating a single instance of OrderService
    if not hasattr(get_order_service, "_instance"):
        get_order_service._instance = OrderService()
    return get_order_service._instance
