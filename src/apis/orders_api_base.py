# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictInt, StrictStr, field_validator
from typing import Optional
from typing_extensions import Annotated
from my_package.models.error_response import ErrorResponse
from my_package.models.order_request import OrderRequest
from my_package.models.order_response import OrderResponse
from my_package.models.orders_list_response import OrdersListResponse
from my_package.security_api import get_token_ApiKeyAuth

class BaseOrdersApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseOrdersApi.subclasses = BaseOrdersApi.subclasses + (cls,)
    async def cancel_order(
        self,
        order_id: Annotated[StrictStr, Field(description="Unique identifier for the order")],
    ) -> OrderResponse:
        ...


    async def create_order(
        self,
        order_request: Annotated[OrderRequest, Field(description="Order creation payload")],
    ) -> OrderResponse:
        ...


    async def get_order(
        self,
        order_id: Annotated[StrictStr, Field(description="Unique identifier for the order")],
    ) -> OrderResponse:
        ...


    async def list_orders(
        self,
        status: Annotated[Optional[StrictStr], Field(description="Filter orders by status")],
        limit: Annotated[Optional[StrictInt], Field(description="Number of orders to return")],
        offset: Annotated[Optional[StrictInt], Field(description="Pagination offset")],
    ) -> OrdersListResponse:
        ...
