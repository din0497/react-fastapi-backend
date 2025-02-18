import pytest
from fastapi import status
from models.order import Order, OrderStatus
import json
from datetime import datetime


@pytest.mark.asyncio
async def test_create_order_success(test_client, mock_order_service, mock_connection_manager):
    # Test data
    order_data = {
        "foodName": "Pizza",
        "quantity": 2
    }

    # Mock response
    mock_order = Order(
        id="12345",
        foodName="Pizza",
        quantity=2,
        status=OrderStatus.PENDING,
        timestamp=datetime.now()
    )

    # Setup mock
    mock_order_service.create_order.return_value = mock_order
    mock_connection_manager.broadcast.return_value = None

    # Make request
    response = test_client.post("/order", json=order_data)

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["foodName"] == "Pizza"
    assert response_data["quantity"] == 2
    assert response_data["status"] == OrderStatus.PENDING.value

    # Verify mock calls
    mock_order_service.create_order.assert_called_once()
    mock_connection_manager.broadcast.assert_called_once()


@pytest.mark.asyncio
async def test_get_orders(test_client, mock_order_service):
    # Mock response
    mock_orders = [
        Order(id="1", foodName="Pizza", quantity=1, status=OrderStatus.PENDING),
        Order(id="2", foodName="Burger", quantity=2, status=OrderStatus.PREPARING)
    ]

    # Setup mock
    mock_order_service.get_orders.return_value = mock_orders

    # Make request
    response = test_client.get("/orders")

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["foodName"] == "Pizza"
    assert response_data[1]["foodName"] == "Burger"
