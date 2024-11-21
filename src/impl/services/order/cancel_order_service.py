# impl/services/order/cancel_order_service.py

import logging
from fastapi import HTTPException
from traceback import format_exc
from models.order_response import OrderResponse

logger = logging.getLogger(__name__)

class CancelOrderService:
    def __init__(self, order_id, dependencies):
        self.order_id = order_id
        self.dependencies = dependencies
        self.response = None

        logger.debug("Inside CancelOrderService")

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

            # Cancel the order
            order_object = order_repository.cancel_order(order_id=self.order_id)

            if not order_object:
                # Determine if the order was not found or cannot be cancelled
                order_exists = order_repository.get_order(self.order_id)
                if not order_exists:
                    logger.error(f"Order with ID {self.order_id} not found.")
                    raise HTTPException(status_code=404, detail=f"Order with ID {self.order_id} not found.")
                else:
                    logger.error(f"Order with ID {self.order_id} cannot be cancelled. Current status: {order_exists.status}")
                    raise HTTPException(status_code=400, detail=f"Order with ID {self.order_id} cannot be cancelled. Current status: {order_exists.status}")

            logger.debug("Order cancelled successfully")

            # Prepare the preprocessed data
            self.preprocessed_data = {
                "order": order_object,
            }

        except HTTPException as e:
            # Re-raise HTTPExceptions
            raise e
        except Exception as e:
            logger.error(f"An error occurred: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Internal server error")

    def process_request(self):
        order = self.preprocessed_data["order"]

        # Create the OrderResponse
        self.response = OrderResponse(
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
