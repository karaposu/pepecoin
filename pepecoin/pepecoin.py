# pepecoin.py

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from typing import List, Optional
import logging
import time
import threading

logger = logging.getLogger(__name__)


class Pepecoin:
    def __init__(
        self,
        rpc_user: str,
        rpc_password: str,
        host: str = '127.0.0.1',
        port: int = 29373,
        wallet_name: Optional[str] = None
    ):
        """
        Initialize the Pepecoin RPC connection.

        :param rpc_user: RPC username.
        :param rpc_password: RPC password.
        :param host: Host where the Pepecoin node is running.
        :param port: RPC port of the Pepecoin node.
        :param wallet_name: Name of the wallet to interact with (optional).
        """
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.host = host
        self.port = port
        self.wallet_name = wallet_name
        self.rpc_connection = self.init_rpc()

    def init_rpc(self) -> AuthServiceProxy:
        """
        Initialize the RPC connection to the Pepecoin node.

        :return: AuthServiceProxy object.
        """
        try:
            if self.wallet_name:
                rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.host}:{self.port}/wallet/{self.wallet_name}"
            else:
                rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.host}:{self.port}"
            connection = AuthServiceProxy(rpc_url)
            # Test the connection
            connection.getblockchaininfo()
            logger.debug("RPC connection established successfully.")
            return connection
        except JSONRPCException as e:
            logger.error(f"Failed to connect to Pepecoin node: {e}")
            raise e

    def get_blockchain_info(self) -> dict:
        """
        Retrieve blockchain information using RPC.

        :return: A dictionary containing blockchain info.
        """
        try:
            info = self.rpc_connection.getblockchaininfo()
            return info
        except JSONRPCException as e:
            logger.error(f"Error retrieving blockchain info: {e}")
            return {}

    def monitor_node(self, interval: int = 60):
        """
        Continuously monitor the Pepecoin node status at specified intervals.

        :param interval: Time in seconds between status checks.
        """

        def monitor():
            while True:
                info = self.get_blockchain_info()
                if info:
                    print("=== Pepecoin Node Status ===")
                    print(f"Chain: {info.get('chain')}")
                    print(f"Blocks: {info.get('blocks')}")
                    print(f"Headers: {info.get('headers')}")
                    print(f"Verification Progress: {info.get('verificationprogress') * 100:.2f}%")
                    print(f"Synced: {not info.get('initialblockdownload')}")
                    print(f"Difficulty: {info.get('difficulty')}")
                    print(f"Best Block Hash: {info.get('bestblockhash')}")
                    print("============================\n")
                else:
                    print("Failed to retrieve blockchain info.")

                time.sleep(interval)

        # Run the monitor in a separate thread to avoid blocking
        threading.Thread(target=monitor, daemon=True).start()

    def check_node_connection(self) -> bool:
        """
        Check if the node is connected and reachable.

        :return: True if connected, False otherwise.
        """
        try:
            self.rpc_connection.getnetworkinfo()
            logger.debug("Node connection is active.")
            return True
        except JSONRPCException as e:
            logger.error(f"Node connection failed: {e}")
            return False

    def create_new_wallet(self, wallet_name: str, passphrase: str = None, disable_private_keys: bool = False) -> bool:
        """
        Create a new wallet.

        :param wallet_name: Name of the new wallet.
        :param passphrase: Passphrase to encrypt the wallet (optional).
        :param disable_private_keys: If True, the wallet will not contain private keys.
        :return: True if wallet was created successfully, False otherwise.
        """
        try:
            self.rpc_connection.createwallet(wallet_name, disable_private_keys=disable_private_keys)
            if passphrase:
                # Load the wallet to encrypt it
                wallet_rpc = self.get_wallet_rpc(wallet_name)
                wallet_rpc.encryptwallet(passphrase)
            logger.debug(f"Wallet '{wallet_name}' created successfully.")
            return True
        except JSONRPCException as e:
            logger.error(f"Error creating wallet '{wallet_name}': {e}")
            return False

    def get_wallet_rpc(self, wallet_name: str) -> AuthServiceProxy:
        """
        Get an RPC connection for a specific wallet.

        :param wallet_name: Name of the wallet.
        :return: AuthServiceProxy object connected to the wallet.
        """
        rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.host}:{self.port}/wallet/{wallet_name}"
        return AuthServiceProxy(rpc_url)

    def lock_wallet(self, wallet_name: Optional[str] = None):
        """
        Lock the specified wallet.

        :param wallet_name: Name of the wallet to lock. If None, uses the default wallet.
        """
        wallet_rpc = self.get_wallet_rpc(wallet_name or self.wallet_name)
        try:
            wallet_rpc.walletlock()
            logger.debug(f"Wallet '{wallet_name}' locked successfully.")
        except JSONRPCException as e:
            logger.error(f"Error locking wallet '{wallet_name}': {e}")

    def unlock_wallet(self, wallet_name: Optional[str], passphrase: str, timeout: int = 60):
        """
        Unlock the specified wallet.

        :param wallet_name: Name of the wallet to unlock.
        :param passphrase: Passphrase of the wallet.
        :param timeout: Time in seconds for which the wallet remains unlocked.
        """
        wallet_rpc = self.get_wallet_rpc(wallet_name or self.wallet_name)
        try:
            wallet_rpc.walletpassphrase(passphrase, timeout)
            logger.debug(f"Wallet '{wallet_name}' unlocked successfully.")
        except JSONRPCException as e:
            logger.error(f"Error unlocking wallet '{wallet_name}': {e}")

    def generate_new_address(self, label: str = None) -> str:
        """
        Generate a new Pepecoin address.

        :param label: Label to associate with the new address (optional).
        :return: The new Pepecoin address.
        """
        try:
            address = self.rpc_connection.getnewaddress(label)
            logger.debug(f"Generated new address: {address}")
            return address
        except JSONRPCException as e:
            logger.error(f"Error generating new address: {e}")
            return ""

    def check_balance(self, wallet_name: Optional[str] = None) -> float:
        """
        Check the balance of the specified wallet.

        :param wallet_name: Name of the wallet to check balance for. If None, uses the default wallet.
        :return: The balance of the wallet.
        """
        wallet_rpc = self.get_wallet_rpc(wallet_name or self.wallet_name)
        try:
            balance = wallet_rpc.getbalance()
            logger.debug(f"Balance for wallet '{wallet_name}': {balance}")
            return balance
        except JSONRPCException as e:
            logger.error(f"Error checking balance for wallet '{wallet_name}': {e}")
            return 0.0

    def check_payment(self, address: str, expected_amount: float, min_confirmations: int = 1) -> bool:
        """
        Check if the expected amount has been received at the specified address.

        :param address: The Pepecoin address to check.
        :param expected_amount: The expected amount to be received.
        :param min_confirmations: Minimum number of confirmations required.
        :return: True if the expected amount has been received, False otherwise.
        """
        try:
            received_amount = self.rpc_connection.getreceivedbyaddress(address, min_confirmations)
            logger.debug(f"Amount received at address '{address}': {received_amount}")
            return received_amount >= expected_amount
        except JSONRPCException as e:
            logger.error(f"Error checking payment for address '{address}': {e}")
            return False

    def mass_transfer(self, from_wallets: List[str], to_address: str, passphrases: Optional[List[str]] = None) -> List[str]:
        """
        Transfer funds from multiple wallets to a target address.

        :param from_wallets: List of wallet names to transfer from.
        :param to_address: The target Pepecoin address to transfer funds to.
        :param passphrases: List of passphrases for the wallets (if encrypted).
        :return: List of transaction IDs.
        """
        tx_ids = []
        for idx, wallet_name in enumerate(from_wallets):
            wallet_rpc = self.get_wallet_rpc(wallet_name)
            passphrase = passphrases[idx] if passphrases and idx < len(passphrases) else None

            try:
                if passphrase:
                    wallet_rpc.walletpassphrase(passphrase, 60)  # Unlock for 60 seconds

                balance = wallet_rpc.getbalance()
                if balance > 0:
                    tx_id = wallet_rpc.sendtoaddress(to_address, balance)
                    tx_ids.append(tx_id)
                    logger.debug(f"Transferred {balance} from wallet '{wallet_name}' to '{to_address}'. TXID: {tx_id}")
                else:
                    logger.debug(f"No balance to transfer from wallet '{wallet_name}'.")

                if passphrase:
                    wallet_rpc.walletlock()
            except JSONRPCException as e:
                logger.error(f"Error transferring from wallet '{wallet_name}': {e}")
        return tx_ids
