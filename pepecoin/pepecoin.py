# pepecoin.py

from indented_logger import setup_logging
import logging
setup_logging(level=logging.INFO, include_func=False, include_module=False)
logger = logging.getLogger(__name__)


from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from typing import Optional, Dict, List
import logging
import threading
import time

# Import the Account class
from .account import Account



class Pepecoin:
    def __init__(
        self,
        rpc_user: str,
        rpc_password: str,
        host: str = '127.0.0.1',
        port: int = 33873,
    ):
        """
        Initialize the Pepecoin node RPC connection.
        """
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.host = host
        self.port = port
        self.rpc_connection = self.init_rpc()
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

    def is_sync_needed(self):
        """Check if the node is synchronized with the network using internal information."""
        try:
            blockchain_info = self.rpc_connection.getblockchaininfo()
            is_initial_download = blockchain_info.get('initialblockdownload', True)
            verification_progress = blockchain_info.get('verificationprogress', 0)

            if not is_initial_download and verification_progress >= 0.9999:
                logger.info("Node is fully synchronized with the network.")
                return False  # Sync is not needed
            else:
                logger.warning("Node is still syncing.")
                logger.warning(f"Verification Progress: {verification_progress * 100:.2f}%")
                return True  # Sync is needed
        except Exception as e:
            logger.error(f"Error checking synchronization status: {e}")
            return True  # Assume sync is needed if there's an error

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

    # ------------------------- Account Management -------------------------

    def generate_new_address(self, account=None):
        if self.is_sync_needed():
            logger.error("Node is not synchronized. Cannot generate a new address.")
            raise Exception("Node is not synchronized with the network.")

        try:
            if account:
                address = self.rpc_connection.getnewaddress(account)
            else:
                address = self.rpc_connection.getnewaddress()
            logger.info(f"Generated new address '{address}' for account '{account}'.")
            return address
        except JSONRPCException as e:
            logger.error(f"Failed to generate new address: {e}")
            return None

    def get_balance(self, account=None):
        try:
            if account:
                balance = self.rpc_connection.getbalance(account)
                logger.info(f"Balance for account '{account}': {balance} PEPE")
            else:
                balance = self.rpc_connection.getbalance()
                logger.info(f"Total wallet balance: {balance} PEPE")
            return balance
        except JSONRPCException as e:
            logger.error(f"Failed to get balance: {e}")
            return None

    def send_from(self, from_account, to_address, amount, minconf=1, comment=None, comment_to=None):
        """Send funds from a specific account to an external address."""
        if self.is_sync_needed():
            logger.error("Node is not synchronized. Cannot proceed with sending funds.")
            raise Exception("Node is not synchronized with the network.")

        try:
            tx_id = self.rpc_connection.sendfrom(from_account, to_address, amount, minconf, comment, comment_to)
            logger.info(f"Sent {amount} PEPE from '{from_account}' to '{to_address}'. Transaction ID: {tx_id}")
            return tx_id
        except JSONRPCException as e:
            logger.error(f"Failed to send from '{from_account}': {e}")
            return None

    def move(self, from_account, to_account, amount, minconf=1, comment=None):
        try:
            result = self.rpc_connection.move(from_account, to_account, amount, minconf, comment)
            if result:
                logger.info(f"Moved {amount} PEPE from '{from_account}' to '{to_account}'.")
            else:
                logger.warning(f"Move operation returned False.")
            return result
        except JSONRPCException as e:
            logger.error(f"Failed to move funds: {e}")
            return False

    def list_accounts(self, minconf=1, include_watchonly=False):
        try:
            accounts = self.rpc_connection.listaccounts(minconf, include_watchonly)
            logger.info("Retrieved list of accounts.")
            return accounts
        except JSONRPCException as e:
            logger.error(f"Failed to list accounts: {e}")
            return {}

    def get_account(self, account_name: str) -> Account:
        """
        Retrieve an Account instance for a given account name.
        """
        return Account(
            rpc_user=self.rpc_user,
            rpc_password=self.rpc_password,
            host=self.host,
            port=self.port,
            account_name=account_name
        )

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

    # ------------------------- Additional Methods Integrated with Account Class -------------------------

    def transfer_between_accounts(
        self,
        from_account_name: str,
        to_account_name: str,
        amount: float,
        comment: str = ""
    ) -> Optional[str]:
        """
        Transfer funds from one account to another.

        :param from_account_name: The name of the account to send funds from.
        :param to_account_name: The name of the account to send funds to.
        :param amount: The amount to transfer.
        :param comment: An optional comment for the transaction.
        :return: The transaction ID if successful, None otherwise.
        """
        try:
            # Get Account instances
            from_account = self.get_account(from_account_name)
            to_account = self.get_account(to_account_name)

            # Generate a new address in the receiving account
            to_address = to_account.generate_address()

            # Send funds to the receiving account's address
            tx_id = self.send_from(
                from_account=from_account_name,
                to_address=to_address,
                amount=amount,
                comment=comment
            )
            logger.info(f"Transferred {amount} PEPE from account '{from_account_name}' to account '{to_account_name}'. TXID: {tx_id}")
            return tx_id
        except JSONRPCException as e:
            logger.error(f"Error transferring funds between accounts: {e}")
            return None

    def mass_transfer_from_accounts(
        self,
        from_account_names: List[str],
        to_address: str,
        amounts: List[float]
    ) -> List[str]:
        """
        Transfer funds from multiple accounts to a single address.

        :param from_account_names: List of account names to transfer from.
        :param to_address: The target Pepecoin address to transfer funds to.
        :param amounts: List of amounts corresponding to each account.
        :return: List of transaction IDs.
        """
        tx_ids = []
        try:
            for idx, account_name in enumerate(from_account_names):
                amount = amounts[idx]
                from_account = self.get_account(account_name)

                tx_id = self.send_from(
                    from_account=account_name,
                    to_address=to_address,
                    amount=amount
                )
                tx_ids.append(tx_id)
                logger.info(f"Transferred {amount} PEPE from account '{account_name}' to '{to_address}'. TXID: {tx_id}")

            return tx_ids
        except JSONRPCException as e:
            logger.error(f"Error in mass transfer from accounts: {e}")
            return tx_ids

    def consolidate_accounts(
        self,
        source_account_names: List[str],
        destination_account_name: str
    ) -> List[str]:
        """
        Consolidate funds from multiple accounts into a single account.

        :param source_account_names: List of account names to transfer from.
        :param destination_account_name: The account name to receive the funds.
        :return: List of transaction IDs.
        """
        tx_ids = []
        try:
            destination_account = self.get_account(destination_account_name)
            destination_address = destination_account.generate_address()

            for account_name in source_account_names:
                source_account = self.get_account(account_name)
                balance = self.get_balance(account_name)
                if balance > 0:
                    tx_id = self.send_from(
                        from_account=account_name,
                        to_address=destination_address,
                        amount=balance
                    )
                    tx_ids.append(tx_id)
                    logger.info(f"Consolidated {balance} PEPE from account '{account_name}' to '{destination_account_name}'. TXID: {tx_id}")
                else:
                    logger.info(f"No balance to transfer from account '{account_name}'.")

            return tx_ids
        except JSONRPCException as e:
            logger.error(f"Error consolidating accounts: {e}")
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
