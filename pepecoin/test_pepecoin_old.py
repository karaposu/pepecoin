# pepecoin/test_pepecoin.py

import os
import time
from pepecoin.pepecoin_old import Pepecoin
import logging

# Configure logging to display info messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pepecoin_class():
    # Initialize the Pepecoin node connection
    pepecoin_node = Pepecoin(
        rpc_user=os.environ.get("RPC_USER", "your_rpc_user"),
        rpc_password=os.environ.get("RPC_PASSWORD", "your_rpc_password"),
        host="127.0.0.1",
        port=33873
    )

    # Test check_node_connection
    print("Testing check_node_connection...")
    node_connected = pepecoin_node.check_node_connection()
    print(f"Node connected: {node_connected}\n")

    # Test get_blockchain_info
    print("Testing get_blockchain_info...")
    blockchain_info = pepecoin_node.get_blockchain_info()
    print(f"Blockchain Info: {blockchain_info}\n")

    # Test get_network_info
    print("Testing get_network_info...")
    network_info = pepecoin_node.get_network_info()
    print(f"Network Info: {network_info}\n")

    # Test get_mempool_info
    print("Testing get_mempool_info...")
    mempool_info = pepecoin_node.get_mempool_info()
    print(f"Mempool Info: {mempool_info}\n")

    # Test get_peer_info
    print("Testing get_peer_info...")
    peer_info = pepecoin_node.get_peer_info()
    print(f"Peer Info: {peer_info}\n")

    # Test get_block_count
    print("Testing get_block_count...")
    block_count = pepecoin_node.get_block_count()
    print(f"Block Count: {block_count}\n")

    # Test get_best_block_hash
    print("Testing get_best_block_hash...")
    best_block_hash = pepecoin_node.get_best_block_hash()
    print(f"Best Block Hash: {best_block_hash}\n")

    # Test get_block_hash
    print("Testing get_block_hash...")
    block_hash = pepecoin_node.get_block_hash(0)  # Genesis block
    print(f"Block Hash at height 0: {block_hash}\n")

    # Test get_block
    print("Testing get_block...")
    block_info = pepecoin_node.get_block(block_hash)
    print(f"Block Info: {block_info}\n")

    # Create accounts and generate addresses
    source_account = "source_account"
    destination_account = "destination_account"

    # Generate addresses for accounts
    print("Generating new address for source account...")
    source_address = pepecoin_node.generate_new_address(account=source_account)
    print(f"New Address for account '{source_account}': {source_address}\n")

    print("Generating new address for destination account...")
    destination_address = pepecoin_node.generate_new_address(account=destination_account)
    print(f"New Address for account '{destination_account}': {destination_address}\n")

    # Get balances
    print("Getting balances for accounts...")
    source_balance = pepecoin_node.get_balance(account=source_account)
    destination_balance = pepecoin_node.get_balance(account=destination_account)
    print(f"Balance for account '{source_account}': {source_balance} PEPE")
    print(f"Balance for account '{destination_account}': {destination_balance} PEPE\n")

    # For testing purposes, ensure the source account has funds
    if source_balance < 0.1:
        print(f"Source account '{source_account}' has insufficient balance. Please send funds to '{source_address}'.")
        return

    # Simulate transferring funds between accounts
    print("Testing transfer between accounts...")
    transfer_amount = 0.01  # Adjust as needed

    # Ensure source account has sufficient balance
    if source_balance >= transfer_amount:
        tx_id = pepecoin_node.send_from(
            from_account=source_account,
            to_address=destination_address,  # Sending to the destination account's address
            amount=transfer_amount,
            comment="Test transfer"
        )
        print(f"Transfer successful. Transaction ID: {tx_id}\n")
    else:
        print(f"Insufficient balance in source account '{source_account}'.\n")

    # Wait for the transaction to be registered
    print("Waiting for the transaction to be registered...")
    time.sleep(10)  # Increase sleep time if necessary

    # Check the balances again
    print("Getting balances after transfer...")
    source_balance = pepecoin_node.get_balance(account=source_account)
    destination_balance = pepecoin_node.get_balance(account=destination_account)
    print(f"Balance for account '{source_account}': {source_balance} PEPE")
    print(f"Balance for account '{destination_account}': {destination_balance} PEPE\n")

    # Test moving funds between accounts without creating a transaction
    print("Testing move between accounts...")
    move_amount = 0.005  # Adjust as needed

    # Ensure source account has sufficient balance
    if source_balance >= move_amount:
        move_result = pepecoin_node.move(
            from_account=source_account,
            to_account=destination_account,
            amount=move_amount,
            comment="Test move"
        )
        if move_result:
            print(f"Move successful. Moved {move_amount} PEPE from '{source_account}' to '{destination_account}'.\n")
        else:
            print("Move failed.\n")
    else:
        print(f"Insufficient balance in source account '{source_account}' for move.\n")

    # Check balances after move
    print("Getting balances after move...")
    source_balance = pepecoin_node.get_balance(account=source_account)
    destination_balance = pepecoin_node.get_balance(account=destination_account)
    print(f"Balance for account '{source_account}': {source_balance} PEPE")
    print(f"Balance for account '{destination_account}': {destination_balance} PEPE\n")

    # List all accounts and their balances
    print("Listing all accounts and balances...")
    accounts = pepecoin_node.list_accounts()
    for acc_name, acc_balance in accounts.items():
        print(f"Account '{acc_name}': {acc_balance} PEPE")
    print()

    print("All tests completed.")


if __name__ == "__main__":
    test_pepecoin_class()
