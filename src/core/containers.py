# here is core/containers.py
from dependency_injector import containers, providers

import logging
logger = logging.getLogger(__name__)
import os

import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from db.repositories.user_repository import UserRepository
# from db.repositories.file_repository import FileRepository
# from db.session import get_engine
#



class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Engine provider
    engine = providers.Singleton(
        create_engine,
        config.db_url,
        echo=False
    )

    # Bank Info Engine provider
    bank_info_engine = providers.Singleton(
        create_engine,
        config.bank_info_db_url,
        echo=False
    )

    # Bank Info Session factory provider
    bank_info_session_factory = providers.Singleton(
        sessionmaker,
        bind=bank_info_engine
    )








