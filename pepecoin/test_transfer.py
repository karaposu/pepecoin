# test_transfer.py

import logging
import sys
import time
from pepecoin import Pepecoin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Initialize Pepecoin node connection
    pepecoin_node = Pepecoin(
        rpc_user='karaposu',
        rpc_password='sanane',
        host='127.0.0.1',
        port=33873
    )

    # Check node connection
    logger.info("Checking node connection...")
    if not pepecoin_node.check_node_connection():
        logger.error("Node is not connected. Exiting.")
        sys.exit(1)

    # Check synchronization status
    logger.info("Checking node synchronization status...")
    if pepecoin_node.is_sync_needed():
        logger.error("Node is not synchronized. Please wait until synchronization is complete.")
        sys.exit(1)

    # Define source account and receiving address
    source_account_name = 'source_account'
    receiving_address = 'Ps8YKEQdZA9aBYmYGSye7Q6yLYir4zMEp5'  # Your consistent test address

    # Get the source account
    source_account = pepecoin_node.get_account(source_account_name)

    # Check balance of source account
    logger.info(f"Retrieving balance for account '{source_account_name}'...")
    balance = pepecoin_node.get_balance(source_account_name)
    if balance is None:
        logger.error(f"Could not retrieve balance for account '{source_account_name}'. Exiting.")
        sys.exit(1)

    if balance <= 0:
        logger.error(f"Source account '{source_account_name}' has insufficient balance ({balance} PEPE).")
        logger.error(f"Please send funds to the source account address to proceed with the test.")
        # Optionally, print an address to send funds to
        source_addresses = source_account.list_addresses()
        if source_addresses:
            logger.info(f"Send funds to the following address: {source_addresses[0]}")
        else:
            new_address = source_account.generate_address()
            logger.info(f"Generated new address for receiving funds: {new_address}")
        sys.exit(1)

    # Define amount to transfer
    amount_to_transfer = 0.1  # Adjust the amount as needed

    if balance < amount_to_transfer:
        logger.error(f"Source account '{source_account_name}' has insufficient balance to transfer {amount_to_transfer} PEPE.")
        sys.exit(1)

    # Perform the transfer
    logger.info(f"Initiating transfer of {amount_to_transfer} PEPE from account '{source_account_name}' to address '{receiving_address}'...")
    tx_id = pepecoin_node.send_from(
        from_account=source_account_name,
        to_address=receiving_address,
        amount=amount_to_transfer,
        comment='Test transfer',
        comment_to='Receiver'
    )

    if tx_id:
        logger.info(f"Transfer successful. Transaction ID: {tx_id}")
    else:
        logger.error("Transfer failed.")

if __name__ == '__main__':
    main()
