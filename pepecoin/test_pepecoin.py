# pepecoin/test_pepecoin.py

import os
import sys
import time
from pepecoin import Pepecoin
import logging

# Configure logging to display info messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from pepecoin.utils import bring_addresses_by_account, get_all_addresses , bring_account_from_address, bring_address_info



def test_pepecoin_class():
    # Initialize the Pepecoin node connection
    pepecoin_node = Pepecoin(
        rpc_user=os.environ.get("RPC_USER", "test"),
        rpc_password=os.environ.get("RPC_PASSWORD", "test"),
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

    
    logger.info("running  get_all_addresses  before new address generation")
    get_all_addresses(pepecoin_node)
    logger.info(" ")


    logger.info("Generating sample  source_address and destination_account")

    try:
    
        source_address = pepecoin_node.generate_new_address(account=source_account)
        destination_account = pepecoin_node.generate_new_address(account=destination_account)

    except Exception as e:
        logger.error("Failed to generate new address due to node synchronization issues or another problem.")
        logger.error(f"Exception: {e}")
        logger.info("Please ensure the node is fully synchronized before running this test.")
        logger.info("If this is new install you should wait a bit and repeat this test.")
        # Decide whether to exit or skip the rest of the tests
        sys.exit(1)
    
    logger.info(" ")
    logger.info("running  get_all_addresses  after new address generation")
    get_all_addresses(pepecoin_node)

    
    
    logger.info("Getting balances for accounts...")
    logger.info(f"Checking for source account with address: {source_address}")
    source_balance = pepecoin_node.get_balance(account=source_account)
    
    logger.info(f"Checking for destination account with address: {destination_account}")
    destination_balance = pepecoin_node.get_balance(account=destination_account)


    logger.info("Core tests completed.")
    logger.info(f"To test the coin transfer functionality please run: ")
    logger.info(f"        pepecoin-transfer-test ")


if __name__ == "__main__":
    test_pepecoin_class()
