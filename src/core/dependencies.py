
# this is core/dependencies.py

from pathlib import Path
from core.containers import  Services
import logging
import logging
logger = logging.getLogger(__name__)
import os

def setup_dependencies():
    base_dir = os.path.dirname(__file__)

    # Paths for the databases
    main_db_path = os.path.join(base_dir, "..", "db", "data", "budget_tracker.db")
    bank_info_db_path = os.path.join(base_dir, "..", "db", "data", "fixed_data.db")
    exchange_rate_db_path = os.path.join(base_dir, "..", "db", "data", "mass_exchange_rate.db")
    fixed_info_db_path = os.path.join(base_dir, "..", "db", "data", "fixed_data.db")

    # Resolve absolute paths
    main_db_path = os.path.abspath(main_db_path)
    bank_info_db_path = os.path.abspath(bank_info_db_path)
    exchange_rate_db_path = os.path.abspath(exchange_rate_db_path)
    fixed_info_db_path = os.path.abspath(fixed_info_db_path)

    # categories_yaml_path = 'assets/config/categories.yaml'

    # Create database URLs
    main_db_url = f"sqlite:///{main_db_path}"
    bank_info_db_url = f"sqlite:///{bank_info_db_path}"
    exchange_rate_db_url = f"sqlite:///{exchange_rate_db_path}"
    fixed_info_db_url = f"sqlite:///{fixed_info_db_path}"

    # Initialize the services container
    services = Services()
    services.config.from_dict({
        'db_url': main_db_url,
        'bank_info_db_url': bank_info_db_url,
        'exchange_rate_db_url': exchange_rate_db_url,
        'fixed_info_db_url': fixed_info_db_url,
    })

    return services


def initialize_services(services):
    # Force initialization by accessing the singleton

    configs = services.configs
    logger.debug(" dependencies initialize_services called")
    logger.debug(f"dummy_path: {configs.config.dummy_path()}")

    #  _ = services.singleton_user_repository()

    logger.info("All models and resources have been loaded and cached")


def main():
    pass



if __name__ == '__main__':
     main()


