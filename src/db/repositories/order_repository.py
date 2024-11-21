# db/repositories/order_repository.py

from sqlalchemy.orm import Session
from db.models.order import Order
from models.order_request import OrderRequest  # Assuming this is your Pydantic model
from uuid import uuid4
import datetime
from pepecoin_rpc import PepecoinRPC
from dotenv import load_dotenv
from typing import List, Optional, Tuple
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

    def get_all_orders(
            self,
            status: Optional[str] = None,
            limit: int = 100,
            offset: int = 0
    ) -> Tuple[List[Order], int]:
        """
        Retrieves a list of orders filtered by status, with pagination support,
        and returns the total count of matching orders.

        :param status: The status to filter orders by (e.g., 'Pending', 'Paid').
                       If None, retrieves orders of all statuses.
        :param limit: The maximum number of orders to return.
        :param offset: The number of orders to skip (for pagination).
        :return: A tuple containing:
                 - A list of Order objects.
                 - The total count of matching orders.
        """
        try:
            # Start building the base query
            query = self.db_session.query(Order)

            # Apply status filter if provided
            if status:
                query = query.filter(Order.status == status)

            # Get the total count before applying limit and offset
            total_count = query.with_entities(func.count()).scalar()

            # Apply ordering, limit, and offset
            orders = (
                query.order_by(Order.created_at.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )

            return orders, total_count
        except Exception as e:
            # Log the exception if needed
            print(f"Error retrieving orders: {e}")
            return [], 0

    def get_order(self, order_id: str) :
        """
        Retrieves an order by its order_id.

        :param order_id: The unique order ID.
        :return: The Order object if found, else None.
        """
        try:
            order = self.session.query(Order).filter(Order.order_id == order_id).first()
            return order
        except Exception as e:
            # Log the exception if needed
            print(f"Error retrieving order with ID {order_id}: {e}")
            return None

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


