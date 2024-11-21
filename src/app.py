
# here is app.py

from indented_logger import setup_logging
import logging
logging.getLogger("passlib").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

setup_logging(level=logging.DEBUG, include_func=True, include_module=False)
logger.debug("start")

from fastapi import FastAPI
from core.dependencies import setup_dependencies
from apis.orders_api import router as OrdersApiRouter
import logging
# from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="Pepecoin Payment Gateway API",
    description="API for paying with Pepecoin",
    version="1.0.0",
)


origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://editor.swagger.io/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins , # Adjust this to more specific domains for security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.include_router(OrdersApiRouter)
services = setup_dependencies()

@app.on_event("startup")
async def startup_event():
    app.state.services = services
    logger.debug("Configurations loaded and services initialized")




