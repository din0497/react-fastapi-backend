# app/api/websocket/manager.py

from fastapi import WebSocket
from typing import Set
import asyncio
import logging
import json
from app.config import settings

logger = logging.getLogger(__name__)


class ConnectionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.active_connections = set()
            cls._instance._lock = asyncio.Lock()
            cls._instance._message_queue = asyncio.Queue(maxsize=settings.ORDER_QUEUE_SIZE)
        return cls._instance

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
            logger.info(
                f"New WebSocket connection from {websocket.client}. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                logger.info(
                    f"WebSocket disconnected from {websocket.client}. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        try:
            message_data = json.loads(message)
            logger.info(
                f"Broadcasting message type: {message_data.get('type')} to {len(self.active_connections)} connections")
        except:
            logger.info(f"Broadcasting message to {len(self.active_connections)} connections")

        # Only do immediate broadcast, don't queue
        await self._broadcast_message(message)

    async def _broadcast_message(self, message: str):
        inactive_connections = set()
        connections_to_process = set(self.active_connections)

        for connection in connections_to_process:
            try:
                await connection.send_text(message)
                logger.debug(f"Successfully sent message to {connection.client}")
            except Exception as e:
                logger.error(f"Error sending message to client {connection.client}: {str(e)}")
                inactive_connections.add(connection)

        if inactive_connections:
            async with self._lock:
                self.active_connections -= inactive_connections
                logger.info(f"Removed {len(inactive_connections)} inactive connections")

    async def process_message_queue(self):
        # This method is now deprecated but kept for compatibility
        # We're not using the queue anymore to avoid double broadcasts
        while True:
            await asyncio.sleep(1)