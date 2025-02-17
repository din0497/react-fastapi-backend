from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Order Management System"
    DEBUG: bool = False
    MAX_CONNECTIONS: int = 1000
    BATCH_SIZE: int = 100
    ORDER_QUEUE_SIZE: int = 1000

    class Config:
        env_file = ".env"

settings = Settings()