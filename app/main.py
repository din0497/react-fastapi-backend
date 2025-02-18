from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import orders
from app.config import settings
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)

@app.on_event("startup")
async def startup_event():

    connection_manager = orders.get_connection_manager()
    asyncio.create_task(connection_manager.process_message_queue())
    logger.info("Message queue processor started.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
