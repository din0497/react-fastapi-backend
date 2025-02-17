from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    RECEIVED = "received"
    PREPARING = "preparing"
    COMPLETED = "completed"

class OrderCreate(BaseModel):
    foodName: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0, le=100)

class Order(OrderCreate):
    id: str
    status: OrderStatus = OrderStatus.PENDING
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "foodName": "Pizza",
                "quantity": 1,
                "status": "received",
                "timestamp": "2024-02-17T12:00:00"
            }
        }

    # Override dict method to ensure datetime fields are serialized properly
    def dict(self, *args, **kwargs):
        order_dict = super().dict(*args, **kwargs)
        # Convert the datetime field to ISO format
        order_dict["timestamp"] = self.timestamp.isoformat() if self.timestamp else None
        return order_dict
