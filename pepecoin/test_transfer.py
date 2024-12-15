# test_transfer.py

from indented_logger import setup_logging
import logging
setup_logging(level=logging.INFO, include_func=False, include_module=False)
logger = logging.getLogger(__name__)

import sys
import time
from pepecoin import Pepecoin
from pepecoin.utils import get_all_addresses
import os



def main():
    # Initialize Pepecoin node connection
    pepecoin_node = Pepecoin(
        rpc_user=     os.environ.get("RPC_USER", "test"),
        rpc_password= os.environ.get("RPC_PASSWORD", "test"),
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
    source_account_name = 'source_account'
    source_account = pepecoin_node.get_account(source_account_name)
    source_addresses = source_account.list_addresses()
    if source_addresses:
        selected_source= source_addresses[0]

    destination_account_name = 'destination_account'
    destination_account = pepecoin_node.get_account(destination_account_name)
    destination_addresses = destination_account.list_addresses()
    if destination_addresses:
        selected_destination= destination_addresses[0]
     
    logger.info(f"selected_source {selected_source}")
    logger.info(f"selected_destination {selected_destination}")

    
    balance =pepecoin_node.get_balance_of_address(selected_source)
    if balance <= 0.1:
        logger.error(f"To test Pepecoin transfer functionality, you must have funds in the '{source_account_name}' account, which you currently do not.")
        logger.info(f"Send 1 pepecoin to : {selected_source}, And rerun this test script" )
        logger.info(f"If you sent already, wait and rerun")
        sys.exit(1)
    else:
        receiving_address= selected_destination
        
        amount_to_transfer=0.1
         # Perform the transfer
        logger.info(f"Initiating transfer of {amount_to_transfer} PEP from account '{source_account_name}' to address '{receiving_address}'...")
        tx_id = pepecoin_node.send_from(
            from_account=source_account_name,
            to_address=receiving_address,
            amount=amount_to_transfer,
            comment='Test transfer',
            comment_to='Receiver'
        )
        
        if tx_id:
            logger.info(f"Transfer successful. Transaction ID: {tx_id}")
            logger.info(f"Please run below command to check balance of destination address. (Repeat unless no balance found)")
            logger.info(f"        pepecoin-cli getreceivedbyaddress '{receiving_address}' ")
            
            logger.info(f"To confirm 0.1 pepecoin is gone from source account, run:  ")
            logger.info(f"        pepecoin-cli getbalance source_account ")
            

            
            
        else:
            logger.error("Transfer failed.")
         
     



if __name__ == '__main__':
    main()
