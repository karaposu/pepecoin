# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from my_package.apis.orders_api_base import BaseOrdersApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from my_package.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictInt, StrictStr, field_validator
from typing import Optional
from typing_extensions import Annotated
from my_package.models.error_response import ErrorResponse
from my_package.models.order_request import OrderRequest
from my_package.models.order_response import OrderResponse
from my_package.models.orders_list_response import OrdersListResponse
from my_package.security_api import get_token_ApiKeyAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/orders/{order_id}",
    responses={
        200: {"model": OrderResponse, "description": "Order successfully cancelled"},
        404: {"model": ErrorResponse, "description": "Order not found"},
    },
    tags=["Orders"],
    summary="Cancel an order",
    response_model_by_alias=True,
)
async def cancel_order(
    order_id: Annotated[StrictStr, Field(description="Unique identifier for the order")] = Path(..., description="Unique identifier for the order"),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> OrderResponse:
    if not BaseOrdersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrdersApi.subclasses[0]().cancel_order(order_id)


@router.post(
    "/orders",
    responses={
        201: {"model": OrderResponse, "description": "Order successfully created"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
    },
    tags=["Orders"],
    summary="Create a new order",
    response_model_by_alias=True,
)
async def create_order(
    order_request: Annotated[OrderRequest, Field(description="Order creation payload")] = Body(None, description="Order creation payload"),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> OrderResponse:
    if not BaseOrdersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrdersApi.subclasses[0]().create_order(order_request)


@router.get(
    "/orders/{order_id}",
    responses={
        200: {"model": OrderResponse, "description": "Order details retrieved successfully"},
        404: {"model": ErrorResponse, "description": "Order not found"},
    },
    tags=["Orders"],
    summary="Retrieve order details",
    response_model_by_alias=True,
)
async def get_order(
    order_id: Annotated[StrictStr, Field(description="Unique identifier for the order")] = Path(..., description="Unique identifier for the order"),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> OrderResponse:
    if not BaseOrdersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrdersApi.subclasses[0]().get_order(order_id)


@router.get(
    "/orders",
    responses={
        200: {"model": OrdersListResponse, "description": "List of orders"},
    },
    tags=["Orders"],
    summary="List all orders",
    response_model_by_alias=True,
)
async def list_orders(
    status: Annotated[Optional[StrictStr], Field(description="Filter orders by status")] = Query(None, description="Filter orders by status", alias="status"),
    limit: Annotated[Optional[StrictInt], Field(description="Number of orders to return")] = Query(20, description="Number of orders to return", alias="limit"),
    offset: Annotated[Optional[StrictInt], Field(description="Pagination offset")] = Query(0, description="Pagination offset", alias="offset"),
    token_ApiKeyAuth: TokenModel = Security(
        get_token_ApiKeyAuth
    ),
) -> OrdersListResponse:
    if not BaseOrdersApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseOrdersApi.subclasses[0]().list_orders(status, limit, offset)
