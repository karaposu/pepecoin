# pepecoin.py

#

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from typing import Optional, Dict, List
import logging
import threading
import time

# Import the Wallet class
from .wallet import Wallet

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Pepecoin:
    def __init__(
        self,
        rpc_user: str,
        rpc_password: str,
        host: str = '127.0.0.1',
        port: int = 29373,
    ):
        """
        Initialize the Pepecoin node RPC connection.
        """
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.host = host
        self.port = port
        self.rpc_connection = self.init_rpc()
        self.wallets = {}  # Dictionary to store Wallet instances
        logger.debug("Initialized Pepecoin node RPC connection.")

    def init_rpc(self) -> AuthServiceProxy:
        """
        Initialize the RPC connection to the Pepecoin node.
        """
        try:
            rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.host}:{self.port}"
            connection = AuthServiceProxy(rpc_url)
            # Test the connection
            connection.getblockchaininfo()
            logger.info("RPC connection to Pepecoin node established successfully.")
            return connection
        except JSONRPCException as e:
            logger.error(f"Failed to connect to Pepecoin node: {e}")
            raise e

    # ------------------------- Node Management -------------------------

    def check_node_connection(self) -> bool:
        """
        Check if the node is connected and reachable.
        """
        try:
            self.rpc_connection.getnetworkinfo()
            logger.info("Node connection is active.")
            return True
        except JSONRPCException as e:
            logger.error(f"Node connection failed: {e}")
            return False

    def get_blockchain_info(self) -> Dict:
        """
        Retrieve blockchain information using RPC.
        """
        try:
            info = self.rpc_connection.getblockchaininfo()
            logger.info("Retrieved blockchain info.")
            return info
        except JSONRPCException as e:
            logger.error(f"Error retrieving blockchain info: {e}")
            raise e

    def monitor_node(self, interval: int = 60):
        """
        Continuously monitor the Pepecoin node status at specified intervals.
        """

        def monitor():
            while True:
                try:
                    info = self.get_blockchain_info()
                    print("=== Pepecoin Node Status ===")
                    print(f"Chain: {info.get('chain')}")
                    print(f"Blocks: {info.get('blocks')}")
                    print(f"Headers: {info.get('headers')}")
                    print(f"Verification Progress: {info.get('verificationprogress') * 100:.2f}%")
                    print(f"Synced: {not info.get('initialblockdownload')}")
                    print(f"Difficulty: {info.get('difficulty')}")
                    print(f"Best Block Hash: {info.get('bestblockhash')}")
                    print("============================\n")
                except JSONRPCException as e:
                    logger.error(f"Error during node monitoring: {e}")

                time.sleep(interval)

        # Run the monitor in a separate thread to avoid blocking
        threading.Thread(target=monitor, daemon=True).start()

    # ------------------------- Wallet Management -------------------------

    def create_new_wallet(
        self,
        wallet_name: str,
        passphrase: Optional[str] = None,
        disable_private_keys: bool = False
    ) -> Optional['Wallet']:
        """
        Create a new wallet and return a Wallet instance.
        """
        try:
            # Check if wallet already exists
            existing_wallets = self.rpc_connection.listwalletdir()['wallets']
            wallet_paths = [wallet['name'] for wallet in existing_wallets]
            if wallet_name in wallet_paths:
                logger.warning(f"Wallet '{wallet_name}' already exists.")
                return self.get_wallet(wallet_name)

            self.rpc_connection.createwallet(wallet_name, disable_private_keys=disable_private_keys)
            logger.info(f"Wallet '{wallet_name}' created successfully.")
            wallet_rpc = self.get_wallet_rpc(wallet_name)
            if passphrase:
                # Encrypt the wallet
                wallet_rpc.encryptwallet(passphrase)
                logger.info(f"Wallet '{wallet_name}' encrypted successfully.")
                # Need to re-initialize the wallet RPC connection after encryption
                time.sleep(2)  # Wait for the wallet to be fully encrypted and reloaded
                wallet_rpc = self.get_wallet_rpc(wallet_name)

            # Create a Wallet instance
            wallet = Wallet(
                rpc_user=self.rpc_user,
                rpc_password=self.rpc_password,
                host=self.host,
                port=self.port,
                wallet_name=wallet_name
            )
            # Store the Wallet instance for future use
            self.wallets[wallet_name] = wallet
            return wallet
        except JSONRPCException as e:
            logger.error(f"Error creating wallet '{wallet_name}': {e}")
            return None

    def load_wallet(self, wallet_name: str) -> Optional['Wallet']:
        """
        Load a wallet into the node and return a Wallet instance.
        """
        try:
            self.rpc_connection.loadwallet(wallet_name)
            logger.info(f"Wallet '{wallet_name}' loaded successfully.")
            # Create a Wallet instance
            wallet = Wallet(
                rpc_user=self.rpc_user,
                rpc_password=self.rpc_password,
                host=self.host,
                port=self.port,
                wallet_name=wallet_name
            )
            # Store the Wallet instance for future use
            self.wallets[wallet_name] = wallet
            return wallet
        except JSONRPCException as e:
            logger.error(f"Error loading wallet '{wallet_name}': {e}")
            return None

    def unload_wallet(self, wallet_name: str) -> bool:
        """
        Unload a wallet from the node.
        """
        try:
            self.rpc_connection.unloadwallet(wallet_name)
            logger.info(f"Wallet '{wallet_name}' unloaded successfully.")
            # Remove the Wallet instance from the registry
            if wallet_name in self.wallets:
                del self.wallets[wallet_name]
            return True
        except JSONRPCException as e:
            logger.error(f"Error unloading wallet '{wallet_name}': {e}")
            return False

    def list_wallets(self) -> List[str]:
        """
        List all loaded wallets.
        """
        try:
            wallets = self.rpc_connection.listwallets()
            logger.info(f"Retrieved list of wallets: {wallets}")
            return wallets
        except JSONRPCException as e:
            logger.error(f"Error listing wallets: {e}")
            raise e

    def get_wallet(self, wallet_name: str) -> Optional['Wallet']:
        """
        Retrieve a Wallet instance for a given wallet name.
        """
        if wallet_name in self.wallets:
            return self.wallets[wallet_name]
        else:
            # Attempt to load the wallet if not already loaded
            return self.load_wallet(wallet_name)

    def get_wallet_rpc(self, wallet_name: str) -> AuthServiceProxy:
        """
        Get an RPC connection for a specific wallet.
        """
        rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.host}:{self.port}/wallet/{wallet_name}"
        return AuthServiceProxy(rpc_url)

    # ------------------------- Network Information -------------------------

    def get_network_info(self) -> Dict:
        """
        Get information about the node's connection to the network.
        """
        try:
            info = self.rpc_connection.getnetworkinfo()
            logger.info("Retrieved network info.")
            return info
        except JSONRPCException as e:
            logger.error(f"Error retrieving network info: {e}")
            raise e

    def get_mempool_info(self) -> Dict:
        """
        Get information about the node's transaction memory pool.
        """
        try:
            info = self.rpc_connection.getmempoolinfo()
            logger.info("Retrieved mempool info.")
            return info
        except JSONRPCException as e:
            logger.error(f"Error retrieving mempool info: {e}")
            raise e

    # ------------------------- Utility Methods -------------------------

    def stop_node(self) -> bool:
        """
        Stop the Pepecoin node.
        """
        try:
            self.rpc_connection.stop()
            logger.info("Pepecoin node stopping...")
            return True
        except JSONRPCException as e:
            logger.error(f"Error stopping node: {e}")
            return False

    def get_node_uptime(self) -> int:
        """
        Get the uptime of the Pepecoin node.
        """
        try:
            uptime = self.rpc_connection.uptime()
            logger.info(f"Node uptime: {uptime} seconds.")
            return uptime
        except JSONRPCException as e:
            logger.error(f"Error retrieving node uptime: {e}")
            raise e

    def add_node(self, node_address: str, command: str = 'add') -> bool:
        """
        Attempt to add or remove a node from the addnode list.
        """
        try:
            self.rpc_connection.addnode(node_address, command)
            logger.info(f"Node '{node_address}' {command}ed successfully.")
            return True
        except JSONRPCException as e:
            logger.error(f"Error executing addnode command: {e}")
            return False

    def get_peer_info(self) -> List[Dict]:
        """
        Get information about connected peers.
        """
        try:
            peers = self.rpc_connection.getpeerinfo()
            logger.info(f"Retrieved information on {len(peers)} peers.")
            return peers
        except JSONRPCException as e:
            logger.error(f"Error retrieving peer info: {e}")
            raise e

    # ------------------------- Blockchain Methods -------------------------

    def get_block_count(self) -> int:
        """
        Get the number of blocks in the longest blockchain.
        """
        try:
            count = self.rpc_connection.getblockcount()
            logger.info(f"Current block count: {count}")
            return count
        except JSONRPCException as e:
            logger.error(f"Error retrieving block count: {e}")
            raise e

    def get_best_block_hash(self) -> str:
        """
        Get the hash of the best (tip) block in the longest blockchain.
        """
        try:
            block_hash = self.rpc_connection.getbestblockhash()
            logger.info(f"Best block hash: {block_hash}")
            return block_hash
        except JSONRPCException as e:
            logger.error(f"Error retrieving best block hash: {e}")
            raise e

    def get_block_hash(self, height: int) -> str:
        """
        Get the hash of the block at a given height.
        """
        try:
            block_hash = self.rpc_connection.getblockhash(height)
            logger.info(f"Block hash at height {height}: {block_hash}")
            return block_hash
        except JSONRPCException as e:
            logger.error(f"Error retrieving block hash at height {height}: {e}")
            raise e

    def get_block(self, block_hash: str) -> Dict:
        """
        Get detailed information about a block.
        """
        try:
            block_info = self.rpc_connection.getblock(block_hash)
            logger.info(f"Retrieved block info for hash {block_hash}.")
            return block_info
        except JSONRPCException as e:
            logger.error(f"Error retrieving block info for hash {block_hash}: {e}")
            raise e

    # ------------------------- Fee Estimation -------------------------

    def estimate_smart_fee(self, conf_target: int, estimate_mode: str = 'CONSERVATIVE') -> Dict:
        """
        Estimates the approximate fee per kilobyte needed for a transaction to begin
        confirmation within conf_target blocks.
        """
        try:
            fee_estimate = self.rpc_connection.estimatesmartfee(conf_target, estimate_mode)
            logger.info(f"Estimated fee: {fee_estimate}")
            return fee_estimate
        except JSONRPCException as e:
            logger.error(f"Error estimating smart fee: {e}")
            raise e

    # ------------------------- Raw Transaction Handling -------------------------

    def send_raw_transaction(self, hex_string: str) -> str:
        """
        Submits raw transaction (serialized, hex-encoded) to local node and network.
        """
        try:
            tx_id = self.rpc_connection.sendrawtransaction(hex_string)
            logger.info(f"Sent raw transaction. TXID: {tx_id}")
            return tx_id
        except JSONRPCException as e:
            logger.error(f"Error sending raw transaction: {e}")
            raise e

    def get_raw_transaction(self, txid: str, verbose: bool = True) -> Dict:
        """
        Return the raw transaction data.
        """
        try:
            transaction = self.rpc_connection.getrawtransaction(txid, verbose)
            logger.info(f"Retrieved raw transaction for TXID: {txid}")
            return transaction
        except JSONRPCException as e:
            logger.error(f"Error retrieving raw transaction for TXID {txid}: {e}")
            raise e

    # ------------------------- Additional Methods Integrated with Wallet Class -------------------------

    def transfer_between_wallets(
        self,
        from_wallet_name: str,
        to_wallet_name: str,
        amount: float,
        passphrase: Optional[str] = None,
        comment: str = ""
    ) -> Optional[str]:
        """
        Transfer funds from one wallet to another.

        :param from_wallet_name: The name of the wallet to send funds from.
        :param to_wallet_name: The name of the wallet to send funds to.
        :param amount: The amount to transfer.
        :param passphrase: The passphrase for the sending wallet, if encrypted.
        :param comment: An optional comment for the transaction.
        :return: The transaction ID if successful, None otherwise.
        """
        try:
            # Get Wallet instances
            from_wallet = self.get_wallet(from_wallet_name)
            to_wallet = self.get_wallet(to_wallet_name)

            if not from_wallet or not to_wallet:
                logger.error("One or both wallets could not be loaded.")
                return None

            # Generate a new address in the receiving wallet
            to_address = to_wallet.generate_address()

            # Unlock the sending wallet if passphrase is provided
            if passphrase:
                from_wallet.unlock_wallet(passphrase=passphrase, timeout=60)

            # Send funds to the receiving wallet's address
            tx_id = from_wallet.send_to_address(
                address=to_address,
                amount=amount,
                comment=comment
            )
            logger.info(f"Transferred {amount} PEPE from '{from_wallet_name}' to '{to_wallet_name}'. TXID: {tx_id}")

            # Lock the sending wallet if it was unlocked
            if passphrase:
                from_wallet.lock_wallet()

            return tx_id
        except JSONRPCException as e:
            logger.error(f"Error transferring funds between wallets: {e}")
            return None

    def mass_transfer_from_wallets(
        self,
        from_wallet_names: List[str],
        to_address: str,
        amounts: List[float],
        passphrases: Optional[List[str]] = None
    ) -> List[str]:
        """
        Transfer funds from multiple wallets to a single address.

        :param from_wallet_names: List of wallet names to transfer from.
        :param to_address: The target Pepecoin address to transfer funds to.
        :param amounts: List of amounts corresponding to each wallet.
        :param passphrases: List of passphrases for the wallets (if encrypted).
        :return: List of transaction IDs.
        """
        tx_ids = []
        try:
            for idx, wallet_name in enumerate(from_wallet_names):
                amount = amounts[idx]
                passphrase = passphrases[idx] if passphrases and idx < len(passphrases) else None
                from_wallet = self.get_wallet(wallet_name)

                if not from_wallet:
                    logger.error(f"Wallet '{wallet_name}' could not be loaded.")
                    continue

                if passphrase:
                    from_wallet.unlock_wallet(passphrase=passphrase, timeout=60)

                tx_id = from_wallet.send_to_address(
                    address=to_address,
                    amount=amount
                )
                tx_ids.append(tx_id)
                logger.info(f"Transferred {amount} PEPE from '{wallet_name}' to '{to_address}'. TXID: {tx_id}")

                if passphrase:
                    from_wallet.lock_wallet()

            return tx_ids
        except JSONRPCException as e:
            logger.error(f"Error in mass transfer from wallets: {e}")
            return tx_ids

    def consolidate_wallets(
        self,
        source_wallet_names: List[str],
        destination_wallet_name: str,
        passphrases: Optional[List[str]] = None
    ) -> List[str]:
        """
        Consolidate funds from multiple wallets into a single wallet.

        :param source_wallet_names: List of wallet names to transfer from.
        :param destination_wallet_name: The wallet name to receive the funds.
        :param passphrases: List of passphrases for the source wallets (if encrypted).
        :return: List of transaction IDs.
        """
        tx_ids = []
        try:
            destination_wallet = self.get_wallet(destination_wallet_name)
            if not destination_wallet:
                logger.error(f"Destination wallet '{destination_wallet_name}' could not be loaded.")
                return tx_ids

            destination_address = destination_wallet.generate_address()

            for idx, wallet_name in enumerate(source_wallet_names):
                passphrase = passphrases[idx] if passphrases and idx < len(passphrases) else None
                source_wallet = self.get_wallet(wallet_name)

                if not source_wallet:
                    logger.error(f"Source wallet '{wallet_name}' could not be loaded.")
                    continue

                if passphrase:
                    source_wallet.unlock_wallet(passphrase=passphrase, timeout=60)

                balance = source_wallet.get_balance()
                if balance > 0:
                    tx_id = source_wallet.send_to_address(
                        address=destination_address,
                        amount=balance
                    )
                    tx_ids.append(tx_id)
                    logger.info(f"Consolidated {balance} PEPE from '{wallet_name}' to '{destination_wallet_name}'. TXID: {tx_id}")
                else:
                    logger.info(f"No balance to transfer from wallet '{wallet_name}'.")

                if passphrase:
                    source_wallet.lock_wallet()

            return tx_ids
        except JSONRPCException as e:
            logger.error(f"Error consolidating wallets: {e}")
            return tx_ids

    # ------------------------- Node Control Methods -------------------------

    def restart_node(self) -> bool:
        """
        Restart the Pepecoin node.
        """
        try:
            self.stop_node()
            logger.info("Waiting for node to shut down...")
            time.sleep(10)  # Wait for the node to shut down
            # Since we can't start the node via RPC, this would require system-level access
            # You can implement this method based on your system setup
            logger.info("Node restart functionality is system-dependent and needs to be implemented.")
            return True
        except Exception as e:
            logger.error(f"Error restarting node: {e}")
            return False
