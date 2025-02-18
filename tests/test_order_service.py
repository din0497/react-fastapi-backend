import pytest
from services.order_service import OrderService
from models.order import OrderStatus
from app.exceptions import OrderNotFoundError, InvalidOrderStatusError


@pytest.mark.asyncio
async def test_create_order():
    service = OrderService()
    order_data = {
        "foodName": "Pizza",
        "quantity": 2
    }

    order = await service.create_order(order_data)

    assert order.foodName == "Pizza"
    assert order.quantity == 2
    assert order.status == OrderStatus.PENDING
    assert isinstance(order.id, str)
    assert len(service.orders) == 1


@pytest.mark.asyncio
async def test_update_order_status():
    service = OrderService()

    # Create test order
    order_data = {"foodName": "Pizza", "quantity": 1}
    order = await service.create_order(order_data)

    # Update status
    updated_order = await service.update_order_status(
        order.id,
        OrderStatus.PREPARING.value
    )

    assert updated_order.status == OrderStatus.PREPARING
    assert service.orders[0].status == OrderStatus.PREPARING


@pytest.mark.asyncio
async def test_invalid_order_status():
    service = OrderService()
    order_data = {"foodName": "Pizza", "quantity": 1}
    order = await service.create_order(order_data)

    with pytest.raises(InvalidOrderStatusError):
        await service.update_order_status(order.id, "invalid_status")