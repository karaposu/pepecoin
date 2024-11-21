# db/repositories/order_repository.py

from sqlalchemy.orm import Session
from db.models.order import Order
from models.order_request import OrderRequest  # Assuming this is your Pydantic model
from uuid import uuid4
import datetime
from pepecoin_rpc import PepecoinRPC
from dotenv import load_dotenv
import os

class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

        # Load environment variables
        load_dotenv()
        rpc_user = os.getenv("RPC_USER")
        rpc_password = os.getenv("RPC_PASSWORD")

        # Initialize Pepecoin RPC client
        self.pepecoin_rpc = PepecoinRPC(rpc_user, rpc_password)

    def create_order(self, order_id: str, payment_address: str, amount_due: float, expires_at: datetime.datetime, metadata: dict) -> Order:
        """
        Creates a new order and saves it to the database.

        :param order_id: The unique order ID.
        :param payment_address: The payment address for the order.
        :param amount_due: The amount due for the order.
        :param expires_at: The expiration datetime for the order.
        :param metadata: Additional metadata for the order.
        :return: The created Order object.
        """
        # Create Order instance
        order = Order(
            order_id=order_id,
            payment_address=payment_address,
            amount_due=amount_due,
            amount_paid=0.0,
            status='Pending',
            created_at=datetime.datetime.utcnow(),
            expires_at=expires_at,
            order_metadata=metadata
        )

        # Add the order to the session and commit
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)

        return order


