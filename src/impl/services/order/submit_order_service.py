# impl/services/order/submit_order_service.py



import logging
from fastapi import HTTPException
from datetime import datetime,timedelta
import os
import tempfile
from traceback import format_exc
from models.order_response import OrderResponse
from pepecoin_rpc import PepecoinRPC
from uuid import uuid4
from dotenv import load_dotenv
import yaml


logger = logging.getLogger(__name__)




class SubmitOrderService:
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None

        self.pepecoin = self.dependencies.pepecoin_factory()

        logger.debug("Inside SubmitOrderService")

        self.preprocess_request_data()
        self.process_request()

        self.is_first_upload=None



    def preprocess_request_data(self):

        amount = self.request.amount
        currency = self.request.currency
        description = self.request.description
        customer_email = self.request.customer_email
        order_metadata = self.request.order_metadata

        logger.debug("Inside preprocess_request_data")

        try:
            logger.debug("Accessing session_factory and repositories from dependencies")
            main_session_factory = self.dependencies.session_factory
            order_repository_provider = self.dependencies.order_repository
            main_sessionmaker = main_session_factory()
            main_session = main_sessionmaker()

            order_repository = order_repository_provider(session=main_session)

            # Generate a unique order ID
            order_id = f"ord_{uuid4().hex}"


            payment_address = self.pepecoin.generate_new_address(label=order_id)


            if not payment_address:
                raise Exception("Failed to generate payment address.")

            # Calculate expiration time (e.g., 1 hour from now)
            expires_at = datetime.utcnow() + timedelta(hours=1)

            # Create the order in the database
            order_object = order_repository.create_order(
                order_id=order_id,
                payment_address=payment_address,
                amount_due=self.request.amount,
                expires_at=expires_at,
                metadata=self.request.order_metadata
            )

            logger.debug("Order created successfully")

            # Prepare the preprocessed data
            self.preprocessed_data = {
                "order": order_object,
                "upload_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"An error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")


    def process_request(self):
        # Build the response using the preprocessed data
        order = self.preprocessed_data["order"]

        self.response = OrderResponse(
            order_id=order.order_id,
            payment_address=order.payment_address,
            amount_due=order.amount_due,
            amount_paid=order.amount_paid,
            status=order.status,
            created_at=order.created_at,
            expires_at=order.expires_at,
            transactions=[],  # You can populate this if needed
            order_metadata=order.order_metadata
        )

