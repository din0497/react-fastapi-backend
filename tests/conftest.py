import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from unittest.mock import AsyncMock, patch
from datetime import datetime
from app.main import app
from services.order_service import OrderService
from app.api.websocket.manager import ConnectionManager

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_order_service():
    with patch('app.api.routes.orders.get_order_service') as mock:
        service = AsyncMock(spec=OrderService)
        mock.return_value = service
        yield service

@pytest.fixture
def mock_connection_manager():
    with patch('app.api.routes.orders.get_connection_manager') as mock:
        manager = AsyncMock(spec=ConnectionManager)
        mock.return_value = manager
        yield manager