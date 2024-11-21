# here is core/containers.py
from dependency_injector import containers, providers

import logging
logger = logging.getLogger(__name__)
import os

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.repositories.order_repository import OrderRepository

from pepecoin import Pepecoin
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()





class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Engine provider
    engine = providers.Singleton(
        create_engine,
        config.db_url,
        echo=False
    )

    # # Retrieve RPC credentials from environment variables
    rpc_user = os.getenv("RPC_USER")
    rpc_password = os.getenv("RPC_PASSWORD")
    #
    # # Initialize the Pepecoin client
    # pepecoin = Pepecoin(rpc_user=rpc_user, rpc_password=rpc_password, wallet_name="merchant_wallet")

    pepecoin_factory = providers.Factory(
        Pepecoin,
        rpc_user=rpc_user,
        rpc_password=rpc_password,
        wallet_name="merchant_wallet"
    )

    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine
    )


    order_repository = providers.Factory(
        OrderRepository,
        session=providers.Dependency()
    )




