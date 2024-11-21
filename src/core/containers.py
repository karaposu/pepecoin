# here is core/containers.py
from dependency_injector import containers, providers

import logging
logger = logging.getLogger(__name__)
import os


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.repositories.user_repository import UserRepository
from db.repositories.file_repository import FileRepository
from db.session import get_engine
import yaml

from db.repositories.bank_information_repository import BankInformationRepository
from db.repositories.report_repository import ReportRepository

from utils.currency_utils import load_currency_configs

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

    bank_information_repository = providers.Factory(
        BankInformationRepository,
        session=providers.Dependency()
    )

    # Session factory provider
    session_factory = providers.Singleton(
        sessionmaker,
        bind=engine
    )

    # UserRepository provider
    user_repository = providers.Factory(
        UserRepository,
        session=providers.Dependency()
    )

    file_repository = providers.Factory(
        FileRepository,
        session=providers.Dependency()
    )

    from db.repositories.record_repository import RecordRepository
    record_repository = providers.Factory(
        RecordRepository,
        session=providers.Dependency()
    )



    #
    # report_repository = providers.Factory(
    #     ReportRepository,
    #     session=providers.Dependency()
    # )

    from db.repositories.exchange_rate_repository import ExchangeRateRepository
    exchange_rate_repository = providers.Factory(
        ExchangeRateRepository,
        session=providers.Dependency()
    )

    exchange_rate_engine = providers.Singleton(
        create_engine,
        config.exchange_rate_db_url,
        echo=False
    )

    fixed_info_engine = providers.Singleton(
        create_engine,
        config.fixed_info_db_url,
        echo=False
    )

    # Exchange Rate Session factory provider
    exchange_rate_session_factory = providers.Singleton(
        sessionmaker,
        bind=exchange_rate_engine
    )

    fixed_info_session_factory = providers.Singleton(
        sessionmaker,
        bind=fixed_info_engine
    )

    # Currency configs provider

    currency_configs = providers.Singleton(
        load_currency_configs,
        yaml_file_path=os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'assets', 'config', 'currencies.yaml'))
    )

    # ReportRepository provider
    report_repository = providers.Factory(
        ReportRepository,
        session=providers.Dependency(),
        currency_configs=currency_configs,
        user_repository=user_repository
    )







