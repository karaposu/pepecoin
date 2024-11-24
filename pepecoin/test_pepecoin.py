# pepecoin/test_pepecoin.py

import os
import time
from pepecoin import Pepecoin
import logging

# Configure logging to display info messages
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_pepecoin_class():
    # Initialize the Pepecoin node connection
    pepecoin_node = Pepecoin(
        rpc_user=os.environ.get("RPC_USER", "karaposu"),
        rpc_password=os.environ.get("RPC_PASSWORD", "sanane"),
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

    # # Test get_node_uptime
    # print("Testing get_node_uptime...")
    # uptime = pepecoin_node.get_node_uptime()
    # print(f"Node Uptime: {uptime} seconds\n")

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

    # # Test estimate_smart_fee
    # print("Testing estimate_smart_fee...")
    # fee_estimate = pepecoin_node.estimate_smart_fee(conf_target=6)
    # print(f"Fee Estimate: {fee_estimate}\n")

    # Test create_new_wallet
    print("Testing create_new_wallet...")
    wallet_name = "test_wallet"
    passphrase = "secure_passphrase"
    wallet = pepecoin_node.create_new_wallet(
        wallet_name=wallet_name,
        passphrase=passphrase,
    )
    if wallet:
        print(f"Wallet '{wallet.wallet_name}' created successfully.\n")
    else:
        print(f"Failed to create wallet '{wallet_name}'.\n")
        return  # Exit the test if wallet creation failed

    # Test get_wallet
    print("Testing get_wallet...")
    retrieved_wallet = pepecoin_node.get_wallet(wallet_name)
    if retrieved_wallet:
        print(f"Wallet '{retrieved_wallet.wallet_name}' retrieved successfully.\n")
    else:
        print(f"Failed to retrieve wallet '{wallet_name}'.\n")

    # Test wallet methods via the retrieved Wallet instance
    print("Testing wallet methods via the retrieved Wallet instance...")

    # Unlock the wallet
    print("Unlocking wallet...")
    retrieved_wallet.unlock_wallet(passphrase=passphrase, timeout=60)
    print("Wallet unlocked.\n")

    # Generate a new address
    print("Generating new address...")
    new_address = retrieved_wallet.generate_address(label="test_label")
    print(f"New Address: {new_address}\n")

    # Get wallet balance
    print("Getting wallet balance...")
    balance = retrieved_wallet.get_balance()
    print(f"Wallet Balance: {balance} PEPE\n")

    # Lock the wallet
    print("Locking wallet...")
    retrieved_wallet.lock_wallet()
    print("Wallet locked.\n")

    # Test unload_wallet
    print("Testing unload_wallet...")
    wallet_unloaded = pepecoin_node.unload_wallet(wallet_name)
    print(f"Wallet unloaded: {wallet_unloaded}\n")

    # Test load_wallet
    print("Testing load_wallet...")
    loaded_wallet = pepecoin_node.load_wallet(wallet_name)
    if loaded_wallet:
        print(f"Wallet '{loaded_wallet.wallet_name}' loaded successfully.\n")
    else:
        print(f"Failed to load wallet '{wallet_name}'.\n")

    # Test transfer_between_wallets
    print("Testing transfer_between_wallets...")
    # Create another wallet to transfer to
    destination_wallet_name = "destination_wallet"
    destination_wallet = pepecoin_node.create_new_wallet(
        wallet_name=destination_wallet_name,
        passphrase=passphrase
    )
    if destination_wallet:
        print(f"Destination wallet '{destination_wallet.wallet_name}' created successfully.\n")
    else:
        print(f"Failed to create destination wallet '{destination_wallet_name}'.\n")
        return

    # Transfer amount (ensure the source wallet has sufficient balance)
    transfer_amount = 0.01  # Adjust as needed
    tx_id = pepecoin_node.transfer_between_wallets(
        from_wallet_name=wallet_name,
        to_wallet_name=destination_wallet_name,
        amount=transfer_amount,
        passphrase=passphrase,
        comment="Test transfer"
    )
    if tx_id:
        print(f"Transfer successful. Transaction ID: {tx_id}\n")
    else:
        print("Transfer failed.\n")

    # Wait for the transaction to be registered
    time.sleep(5)

    # Check the balance of the destination wallet
    print("Checking balance of the destination wallet...")
    dest_balance = destination_wallet.get_balance()
    print(f"Destination Wallet Balance: {dest_balance} PEPE\n")

    # Test mass_transfer_from_wallets
    print("Testing mass_transfer_from_wallets...")
    from_wallet_names = [wallet_name]
    amounts = [0.005]  # Adjust as needed
    passphrases = [passphrase]
    mass_tx_ids = pepecoin_node.mass_transfer_from_wallets(
        from_wallet_names=from_wallet_names,
        to_address=new_address,  # Sending back to the source wallet's address
        amounts=amounts,
        passphrases=passphrases
    )
    print(f"Mass Transfer Transaction IDs: {mass_tx_ids}\n")

    # Wait for the transaction to be registered
    time.sleep(5)

    # Check the balance of the source wallet
    print("Checking balance of the source wallet after mass transfer...")
    source_wallet = pepecoin_node.get_wallet(wallet_name)
    source_balance = source_wallet.get_balance()
    print(f"Source Wallet Balance: {source_balance} PEPE\n")

    # Test consolidate_wallets
    print("Testing consolidate_wallets...")
    source_wallet_names = [wallet_name, destination_wallet_name]
    tx_ids = pepecoin_node.consolidate_wallets(
        source_wallet_names=source_wallet_names,
        destination_wallet_name="consolidated_wallet",
        passphrases=[passphrase, passphrase]
    )
    print(f"Consolidation Transaction IDs: {tx_ids}\n")

    # Wait for the transactions to be registered
    time.sleep(5)

    # Check the balance of the consolidated wallet
    print("Checking balance of the consolidated wallet...")
    consolidated_wallet = pepecoin_node.get_wallet("consolidated_wallet")
    if consolidated_wallet:
        consolidated_balance = consolidated_wallet.get_balance()
        print(f"Consolidated Wallet Balance: {consolidated_balance} PEPE\n")
    else:
        print("Failed to retrieve the consolidated wallet.\n")

    # Test stop_node (optional, be cautious)
    # print("Testing stop_node...")
    # node_stopped = pepecoin_node.stop_node()
    # print(f"Node stopped: {node_stopped}\n")

    print("All tests completed.")

if __name__ == "__main__":
    test_pepecoin_class()
