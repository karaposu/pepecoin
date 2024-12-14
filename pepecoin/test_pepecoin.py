# pepecoin/test_pepecoin.py

import os
import sys
import time
from pepecoin import Pepecoin
import logging

# Configure logging to display info messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_addresses(pepecoin_node):
    """
    Retrieve all addresses known by the node and their total amount received.
    This includes addresses with zero balance, if any.
    """
    try:
        # listreceivedbyaddress( minconf, include_empty ) 
        # minconf=0: include all transactions, even unconfirmed
        # include_empty=True: include addresses that haven't received any payments
        addresses_info = pepecoin_node.rpc_connection.listreceivedbyaddress(0, True)
        all_addresses = {}
        for info in addresses_info:
            address = info['address']
            amount = float(info['amount'])
            all_addresses[address] = amount
        return all_addresses
    except Exception as e:
        logger.error(f"Failed to retrieve addresses: {e}")
        return {}


def test_pepecoin_class():
    # Initialize the Pepecoin node connection
    pepecoin_node = Pepecoin(
        rpc_user=os.environ.get("RPC_USER", "karaposu"),
        rpc_password=os.environ.get("RPC_PASSWORD", "sanane"),
        host="127.0.0.1",
        port=33873
    )


    # Test check_node_connection
    logger.info("Testing check_node_connection...")
    node_connected = pepecoin_node.check_node_connection()
    logger.info(f"Node connected: {node_connected}\n")

    if not node_connected:
        logger.error("Cannot proceed with tests as the node is not connected.")
        return

    # Test get_blockchain_info
    logger.info("Testing get_blockchain_info...")
    blockchain_info = pepecoin_node.get_blockchain_info()
    logger.info(f"Blockchain Info: {blockchain_info}\n")

    # Test get_network_info
    logger.info("Testing get_network_info...")
    network_info = pepecoin_node.get_network_info()
    logger.info(f"Network Info: {network_info}\n")

    # Test get_mempool_info
    logger.info("Testing get_mempool_info...")
    mempool_info = pepecoin_node.get_mempool_info()
    logger.info(f"Mempool Info: {mempool_info}\n")

    # Test get_peer_info
    logger.info("Testing get_peer_info...")
    peer_info = pepecoin_node.get_peer_info()
    logger.info(f"Peer Info: {peer_info}\n")

    # Test get_block_count
    logger.info("Testing get_block_count...")
    block_count = pepecoin_node.get_block_count()
    logger.info(f"Block Count: {block_count}\n")

    # Test get_best_block_hash
    logger.info("Testing get_best_block_hash...")
    best_block_hash = pepecoin_node.get_best_block_hash()
    logger.info(f"Best Block Hash: {best_block_hash}\n")

    # Test get_block_hash
    logger.info("Testing get_block_hash...")
    block_hash = pepecoin_node.get_block_hash(0)  # Genesis block
    logger.info(f"Block Hash at height 0: {block_hash}\n")

    # Test get_block
    logger.info("Testing get_block...")
    block_info = pepecoin_node.get_block(block_hash)
    logger.info(f"Block Info: {block_info}\n")

    # Create accounts and generate addresses
    source_account = "source_account"
    destination_account = "destination_account"


    all_addresses = get_all_addresses(pepecoin_node)


    # Check if there's any previously generated address with a non-zero amount.
    # If you'd like, you could also check for addresses associated to source_account specifically.
    
    for i, (adr, amount) in enumerate(all_addresses.items()):
        if i == 0:
            # Assign on the first address only
            previously_generated_source_address = adr
            previously_generated_source_address_amount = amount
            logger.info(f"Found previously generated address: {adr} with amount: {amount} $PEP (first assigned)")
        else:
            # For subsequent addresses, just log without assigning
            logger.info(f"Found previously generated address: {adr} with amount: {amount} $PEP")
            
        

    
    try:
        if not previously_generated_source_address:
            logger.info("Generating new address for source account...")
            source_address = pepecoin_node.generate_new_address(account=source_account)
            logger.info(f"New Address for '{source_account}': {source_address}\n")
            logger.error(f"To test Pepecoin transfer functionality, you must have funds in the '{source_account}' account, which you currently do not.")
            logger.info(f"Please send 0.1 Pepecoin to the following address to fund your account:\n\n{source_address}\n")
            logger.error("Skipping the transfer step due to insufficient funds.")
            logger.error("Once your source account has some funds, you can rerun this script to continue testing the transfer functionality.")
            sys.exit(1)
        else:
            source_address = previously_generated_source_address
            logger.info("Using previously generated source address")
            logger.info(f"Address for '{source_account}': {source_address}\n")
            if previously_generated_source_address_amount < 0.1:
                logger.error(f"To test Pepecoin transfer functionality, you must have funds in the '{source_account}' account, which you currently do not.")
                logger.error(f"Here is source_account address: {source_address}\n")
                logger.error(f"Please send at least 0.5 pepecoin($PEP) to this address. ")
                logger.error("If you have already sent the funds, they have not been received yet. Please rerun the script after five minutes ")
                sys.exit(1)
          
 
        logger.info("Generating new address for destination account...")
        destination_address = pepecoin_node.generate_new_address(account=destination_account)
        logger.info(f"New Address for '{destination_account}': {destination_address}\n")

    except Exception as e:
        logger.error("Failed to generate new address due to node synchronization issues or another problem.")
        logger.error(f"Exception: {e}")
        logger.info("Please ensure the node is fully synchronized before running this test.")
        logger.info("If this is new install you should wait a bit and repeat this test.")
        # Decide whether to exit or skip the rest of the tests
        sys.exit(1)
    
    # Get balances
    logger.info("Getting balances for accounts...")
    logger.info(f"Checking for source account with address: {source_address}")
    source_balance = pepecoin_node.get_balance(account=source_account)
    
    logger.info(f"Checking for destination account with address: {destination_account}")
    destination_balance = pepecoin_node.get_balance(account=destination_account)
    

    # Define the minimum required balance for testing
    min_required_balance = 0.1  # Adjust as necessary

    # Check if the source account has sufficient funds
    if source_balance < min_required_balance:
        logger.error(f"Source account '{source_account}' has insufficient balance ({source_balance} PEPE).")
        logger.error(f"Please send at least {min_required_balance} $PEP to the source account address '{source_address}' to proceed with the test.")
        logger.error("Skipping tests due to insufficient funds.")
        sys.exit(1)  # Exit the script with an error code

    # Proceed with the rest of the tests
    # Simulate transferring funds between accounts
    logger.info("Testing transfer between accounts...")
    transfer_amount = 0.01  # Adjust as needed

    # Ensure source account has sufficient balance for the transfer amount
    if source_balance >= transfer_amount:
        tx_id = pepecoin_node.send_from(
            from_account=source_account,
            to_address=destination_address,  # Sending to the destination account's address
            amount=transfer_amount,
            comment="Test transfer"
        )
        if tx_id:
            logger.info(f"Transfer successful. Transaction ID: {tx_id}\n")
        else:
            logger.error("Transfer failed.\n")
    else:
        logger.error(f"Insufficient balance in source account '{source_account}' for transfer.")
        logger.error("Skipping transfer test.")
        return

    # Wait for the transaction to be registered
    logger.info("Waiting for the transaction to be registered...")
    time.sleep(10)  # Increase sleep time if necessary

    # Check the balances again
    logger.info("Getting balances after transfer...")
    source_balance = pepecoin_node.get_balance(account=source_account)
    destination_balance = pepecoin_node.get_balance(account=destination_account)
    logger.info(f"Balance for account '{source_account}': {source_balance} PEPE")
    logger.info(f"Balance for account '{destination_account}': {destination_balance} PEPE\n")

    # Test moving funds between accounts without creating a transaction
    logger.info("Testing move between accounts...")
    move_amount = 0.005  # Adjust as needed

    # Ensure source account has sufficient balance for the move amount
    if source_balance >= move_amount:
        move_result = pepecoin_node.move(
            from_account=source_account,
            to_account=destination_account,
            amount=move_amount,
            comment="Test move"
        )
        if move_result:
            logger.info(f"Move successful. Moved {move_amount} PEPE from '{source_account}' to '{destination_account}'.\n")
        else:
            logger.error("Move failed.\n")
    else:
        logger.error(f"Insufficient balance in source account '{source_account}' for move.")
        logger.error("Skipping move test.")
        return

    # Check balances after move
    logger.info("Getting balances after move...")
    source_balance = pepecoin_node.get_balance(account=source_account)
    destination_balance = pepecoin_node.get_balance(account=destination_account)
    logger.info(f"Balance for account '{source_account}': {source_balance} $PEP")
    logger.info(f"Balance for account '{destination_account}': {destination_balance} $PEP\n")

    # List all accounts and their balances
    logger.info("Listing all accounts and balances...")
    accounts = pepecoin_node.list_accounts()
    for acc_name, acc_balance in accounts.items():
        logger.info(f"Account '{acc_name}': {acc_balance} $PEP")
    logger.info("")

    logger.info("All tests completed.")


if __name__ == "__main__":
    test_pepecoin_class()
