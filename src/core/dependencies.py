
# this is core/dependencies.py

from pathlib import Path
from core.containers import Services
import logging
import logging
logger = logging.getLogger(__name__)
import os

def setup_dependencies():
    base_dir = os.path.dirname(__file__)

    # Paths for the databases
    main_db_path = os.path.join(base_dir, "..", "db", "data", "main.db")

    # Resolve absolute paths
    main_db_path = os.path.abspath(main_db_path)


    main_db_url = f"sqlite:///{main_db_path}"


    # Initialize the services container
    services = Services()
    services.config.from_dict({
        'db_url': main_db_url,

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


