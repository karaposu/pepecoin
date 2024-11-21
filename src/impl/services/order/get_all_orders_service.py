# impl/services/order/get_all_orders_service.py

import logging
from fastapi import HTTPException
from datetime import datetime, timedelta
from traceback import format_exc
from models.order_response import OrderResponse
from models.orders_list_response import OrdersListResponse
from uuid import uuid4

logger = logging.getLogger(__name__)

class GetAllOrdersService:
    def __init__(self, status, limit, offset, dependencies):
        self.status = status
        self.limit = limit
        self.offset = offset

        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside GetAllOrdersService")

        self.preprocess_request_data()
        self.process_request()

    def preprocess_request_data(self):
        logger.debug("Inside preprocess_request_data")

        try:
            logger.debug("Accessing session_factory and repositories from dependencies")
            main_session_factory = self.dependencies.session_factory
            order_repository_provider = self.dependencies.order_repository
            main_sessionmaker = main_session_factory()
            main_session = main_sessionmaker()

            order_repository = order_repository_provider(session=main_session)

            # Retrieve the list of orders and total count
            list_of_order_objects, total_count = order_repository.get_all_orders(
                status=self.status,
                limit=self.limit,
                offset=self.offset
            )

            logger.debug("Orders pulled successfully")

            # Prepare the preprocessed data
            self.preprocessed_data = {
                "orders": list_of_order_objects,
                "total_count": total_count,
                "limit": self.limit,
                "offset": self.offset
            }

        except Exception as e:
            logger.error(f"An error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        # Build the response using the preprocessed data
        orders = self.preprocessed_data["orders"]
        total_count = self.preprocessed_data["total_count"]
        limit = self.preprocessed_data["limit"]
        offset = self.preprocessed_data["offset"]

        # Convert the list of Order objects to OrderResponse models
        order_responses = [
            OrderResponse(
                order_id=order.order_id,
                payment_address=order.payment_address,
                amount_due=order.amount_due,
                amount_paid=order.amount_paid,
                status=order.status,
                created_at=order.created_at,
                expires_at=order.expires_at,
                transactions=[],  # Populate if needed
                metadata=order.order_metadata
            )
            for order in orders
        ]

        # Create the OrdersListResponse
        self.response = OrdersListResponse(
            orders=order_responses,
            total_count=total_count
        )
