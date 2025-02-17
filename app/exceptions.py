from fastapi import HTTPException, status

class OrderNotFoundError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

class InvalidOrderStatusError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order status"
        )

class WebSocketConnectionError(Exception):
    pass