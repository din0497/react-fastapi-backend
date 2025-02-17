from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from models.order import OrderCreate, Order, OrderStatus
from services.order_service import OrderService
from app.api.websocket.manager import ConnectionManager
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Create a shared instance of OrderService
order_service_instance = OrderService()


def get_order_service():
    return order_service_instance


def get_connection_manager():
    return ConnectionManager()


class StatusUpdate(BaseModel):
    status: OrderStatus


@router.post("/order", response_model=Order)
async def create_order(
        order: OrderCreate,
        order_service: OrderService = Depends(get_order_service),
        connection_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        new_order = await order_service.create_order(order.dict())
        await connection_manager.broadcast(
            json.dumps({
                "type": "new_order",
                "data": new_order.dict()
            })
        )
        return new_order
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders", response_model=List[Order])
async def get_orders(order_service: OrderService = Depends(get_order_service)):
    try:
        orders = await order_service.get_orders()
        logger.info(f"Fetched {len(orders)} orders")
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/order/{order_id}/status", response_model=Order)
async def update_order_status(
        order_id: str,
        status_update: StatusUpdate,
        order_service: OrderService = Depends(get_order_service),
        connection_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        updated_order = await order_service.update_order_status(
            order_id,
            status_update.status
        )

        await connection_manager.broadcast(
            json.dumps({
                "type": "status_update",
                "data": updated_order.dict()
            })
        )
        return updated_order
    except ValueError as e:
        logger.error(f"Invalid status update: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        order_service: OrderService = Depends(get_order_service),
        connection_manager: ConnectionManager = Depends(get_connection_manager)
):
    try:
        await connection_manager.connect(websocket)

        # Send existing orders as a batch
        orders = await order_service.get_orders()
        await websocket.send_json({
            "type": "initial_orders",
            "data": [order.dict() for order in orders]
        })

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message: {data}")
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected")
                await connection_manager.disconnect(websocket)
                break
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                break
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        await connection_manager.disconnect(websocket)