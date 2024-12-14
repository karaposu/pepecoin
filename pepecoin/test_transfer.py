# test_transfer.py

from indented_logger import setup_logging
import logging
setup_logging(level=logging.INFO, include_func=False, include_module=False)
logger = logging.getLogger(__name__)

import sys
import time
from pepecoin import Pepecoin
from utils import get_all_addresses



def main():
    # Initialize Pepecoin node connection
    pepecoin_node = Pepecoin(
        rpc_user='karaposu',
        rpc_password='sanane',
        host='127.0.0.1',
        port=33873
    )

    # Check node connection
    logger.info("---------------- For transfer test ---------------- ")
    logger.info("Checking node connection...")
    if not pepecoin_node.check_node_connection():
        logger.error("Node is not connected. Exiting.")
        sys.exit(1)

    # Check synchronization status
    logger.info("Checking node synchronization status...")
    if pepecoin_node.is_sync_needed():
        logger.error("Node is not synchronized. Please wait until synchronization is complete.")
        sys.exit(1)


    # get all created addresses
    all_addresses= get_all_addresses(pepecoin_node)


    
    # # Define source and destination accounts
    # source_account_name = 'source_account'
    # destination_account_name = 'destination_account'

    # #find the source account and get addresses 



    # source_addresses = source_account.list_addresses()

    # # Get the source account
    # source_account = pepecoin_node.get_account(source_account_name)

    # # Check balance of source account
    # logger.info(f"--------------------------------")
    # logger.info(f"Retrieving balance for account '{source_account_name}'...")
    # balance = pepecoin_node.get_balance(source_account_name)
    # if balance is None:
    #     logger.error(f"Could not retrieve balance for account '{source_account_name}'. Exiting.")
    #     sys.exit(1)

    # if balance <= 0:
    #     # Get or generate an address for the source account to receive funds
    #     source_addresses = source_account.list_addresses()

    #     if source_addresses:
    #         funding_address = source_addresses[0]
    #         logger.info(f"You should send pepecoin to this already existing address: {funding_address}")
    #     else:
    #         funding_address = source_account.generate_address()
    #         logger.info(f"Generated new address for receiving funds: {funding_address}")

    #     logger.error(f"Source account '{source_account_name}' has insufficient balance ({balance} PEPE).")
    #     logger.error(f"To test Pepecoin transfer functionality, you must have funds in the '{source_account_name}' account, which you currently do not.")
    #     logger.info(f"Please send some Pepecoin to the following address to fund your account:\n\n{funding_address}\n")
    #     logger.error("We did not generate a destination address for you. Once your source account has some funds, you can rerun this script to continue testing the transfer functionality.")
    #     logger.error("Skipping the transfer step due to insufficient funds.")
    #     sys.exit(1)

    # # Define amount to transfer
    # amount_to_transfer = 0.1  # Adjust the amount as needed

    # if balance < amount_to_transfer:
    #     logger.error(f"Source account '{source_account_name}' has insufficient balance to transfer {amount_to_transfer} PEPE.")
    #     sys.exit(1)
    
    # # Get the destination account
    # destination_account = pepecoin_node.get_account(destination_account_name)

    # # Generate a receiving address for the destination account
    # receiving_address = destination_account.generate_address()
    # logger.info(f"Receiving address for account '{destination_account_name}': {receiving_address}")

    # # Perform the transfer
    # logger.info(f"Initiating transfer of {amount_to_transfer} PEPE from account '{source_account_name}' to address '{receiving_address}'...")
    # tx_id = pepecoin_node.send_from(
    #     from_account=source_account_name,
    #     to_address=receiving_address,
    #     amount=amount_to_transfer,
    #     comment='Test transfer',
    #     comment_to='Receiver'
    # )

    # if tx_id:
    #     logger.info(f"Transfer successful. Transaction ID: {tx_id}")
    # else:
    #     logger.error("Transfer failed.")

if __name__ == '__main__':
    main()
