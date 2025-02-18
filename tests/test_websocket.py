import pytest
from fastapi import WebSocket
from app.api.websocket.manager import ConnectionManager
import asyncio
import json


class MockWebSocket:
    def __init__(self):
        self.accepted = False
        self.sent_messages = []
        self.client = "test_client"

    async def accept(self):
        self.accepted = True

    async def send_text(self, message: str):
        self.sent_messages.append(message)


@pytest.mark.asyncio
async def test_websocket_connection():
    websocket = MockWebSocket()
    manager = ConnectionManager()
    manager._lock = asyncio.Lock()
    manager.active_connections = set()

    await manager.connect(websocket)
    assert websocket in manager.active_connections
    assert websocket.accepted == True

    await manager.disconnect(websocket)
    assert websocket not in manager.active_connections


@pytest.mark.asyncio
async def test_broadcast_message():
    websocket1 = MockWebSocket()
    websocket2 = MockWebSocket()
    manager = ConnectionManager()

    manager._lock = asyncio.Lock()
    manager.active_connections = set()


    await manager.connect(websocket1)
    await manager.connect(websocket2)


    test_message = json.dumps({"type": "test", "data": "test_message"})
    await manager.broadcast(test_message)


    assert test_message in websocket1.sent_messages
    assert test_message in websocket2.sent_messages