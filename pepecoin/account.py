# pepecoin/account.py

from typing import List, Dict, Optional
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Account:
    def __init__(
        self,
        rpc_user: str,
        rpc_password: str,
        host: str = '127.0.0.1',
        port: int = 29373,
        account_name: str = ''
    ):
        """
        Initialize the Account instance.

        :param rpc_user: RPC username.
        :param rpc_password: RPC password.
        :param host: RPC host.
        :param port: RPC port.
        :param account_name: The name of the account to manage.
        """
        self.account_name = account_name
        rpc_url = f"http://{rpc_user}:{rpc_password}@{host}:{port}"
        self.rpc_connection = AuthServiceProxy(rpc_url)
        logger.debug(f"Initialized RPC connection for account '{self.account_name}'.")

    # ------------------------- Balance Management -------------------------

    def get_balance(self, min_confirmations: int = 1, include_watchonly: bool = False) -> float:
        """
        Get the account's balance.

        :param min_confirmations: Minimum number of confirmations.
        :param include_watchonly: Include watch-only addresses.

        :return: The account balance.
        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            balance = self.rpc_connection.getbalance(self.account_name, min_confirmations, include_watchonly)
            logger.info(f"Account '{self.account_name}' balance: {balance} PEPE.")
            return balance
        except JSONRPCException as e:
            logger.error(f"Failed to get balance for account '{self.account_name}': {e}")
            raise e

    # ------------------------- Address Management -------------------------

    def generate_address(self) -> str:
        """
        Generate a new Pepecoin address for this account.

        :return: New Pepecoin address.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            address = self.rpc_connection.getnewaddress(self.account_name)
            logger.info(f"Generated new address '{address}' for account '{self.account_name}'.")
            return address
        except JSONRPCException as e:
            logger.error(f"Failed to generate new address for account '{self.account_name}': {e}")
            raise e

    def list_addresses(self) -> List[str]:
        """
        List all addresses associated with this account.

        :return: List of addresses.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            addresses = self.rpc_connection.getaddressesbyaccount(self.account_name)
            logger.info(f"Retrieved addresses for account '{self.account_name}': {addresses}")
            return addresses
        except JSONRPCException as e:
            logger.error(f"Failed to list addresses for account '{self.account_name}': {e}")
            raise e

    # ------------------------- Transaction Management -------------------------

    def list_transactions(
        self,
        count: int = 10,
        skip: int = 0,
        include_watchonly: bool = False
    ) -> List[Dict]:
        """
        List recent transactions for this account.

        :param count: Number of transactions to retrieve.
        :param skip: Number of transactions to skip.
        :param include_watchonly: Include watch-only addresses.
        :return: List of transaction details.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            transactions = self.rpc_connection.listtransactions(self.account_name, count, skip, include_watchonly)
            logger.info(f"Retrieved {len(transactions)} transactions for account '{self.account_name}'.")
            return transactions
        except JSONRPCException as e:
            logger.error(f"Failed to list transactions for account '{self.account_name}': {e}")
            raise e

    def send_to_address(
        self,
        address: str,
        amount: float,
        comment: str = "",
        comment_to: str = ""
    ) -> str:
        """
        Send PEPE from this account to a specified address.

        :param address: Recipient's Pepecoin address.
        :param amount: Amount to send.
        :param comment: Optional comment.
        :param comment_to: Optional comment to the recipient.
        :return: Transaction ID.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            tx_id = self.rpc_connection.sendfrom(self.account_name, address, amount, 1, comment, comment_to)
            logger.info(f"Sent {amount} PEPE from account '{self.account_name}' to '{address}'. Transaction ID: {tx_id}")
            return tx_id
        except JSONRPCException as e:
            logger.error(f"Failed to send to address '{address}' from account '{self.account_name}': {e}")
            raise e

    def move_to_account(
        self,
        to_account: str,
        amount: float,
        comment: str = ""
    ) -> bool:
        """
        Move funds internally between accounts without creating a transaction.

        :param to_account: The account to move funds to.
        :param amount: Amount to move.
        :param comment: Optional comment.
        :return: True if successful, False otherwise.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            result = self.rpc_connection.move(self.account_name, to_account, amount, 1, comment)
            if result:
                logger.info(f"Moved {amount} PEPE from account '{self.account_name}' to account '{to_account}'.")
            else:
                logger.warning(f"Move operation returned False for moving from '{self.account_name}' to '{to_account}'.")
            return result
        except JSONRPCException as e:
            logger.error(f"Failed to move funds from account '{self.account_name}' to '{to_account}': {e}")
            raise e

    # ------------------------- Key Management -------------------------

    def import_private_key(
        self,
        private_key: str,
        rescan: bool = True
    ) -> None:
        """
        Import a private key into the account.

        :param private_key: The private key to import.
        :param rescan: Whether to rescan the blockchain.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.rpc_connection.importprivkey(private_key, self.account_name, rescan)
            logger.info(f"Imported private key into account '{self.account_name}'. Rescan: {rescan}")
        except JSONRPCException as e:
            logger.error(f"Failed to import private key into account '{self.account_name}': {e}")
            raise e

    def export_private_key(self, address: str) -> str:
        """
        Export the private key for a given address.

        :param address: The address to export the key for.
        :return: The private key.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            private_key = self.rpc_connection.dumpprivkey(address)
            logger.info(f"Exported private key for address '{address}'.")
            return private_key
        except JSONRPCException as e:
            logger.error(f"Failed to export private key for address '{address}': {e}")
            raise e

    # ------------------------- Label Management -------------------------

    def set_label(self, address: str, label: str) -> None:
        """
        Assign a label (account name) to an address.

        :param address: The address to label.
        :param label: The label (account name) to assign.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.rpc_connection.setaccount(address, label)
            logger.info(f"Set label '{label}' for address '{address}'.")
        except JSONRPCException as e:
            logger.error(f"Failed to set label for address '{address}': {e}")
            raise e

    def get_label(self, address: str) -> str:
        """
        Retrieve the label (account name) assigned to an address.

        :param address: The address to query.
        :return: The label (account name) of the address.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            label = self.rpc_connection.getaccount(address)
            logger.info(f"Retrieved label '{label}' for address '{address}'.")
            return label
        except JSONRPCException as e:
            logger.error(f"Failed to get label for address '{address}': {e}")
            raise e

    # ------------------------- Payment Monitoring -------------------------

    def check_payment(
        self,
        address: str,
        expected_amount: float,
        min_confirmations: int = 1
    ) -> bool:
        """
        Check if a payment has been received at a specified address.

        :param address: The Pepecoin address to check.
        :param expected_amount: The expected amount to be received.
        :param min_confirmations: Minimum number of confirmations required.

        :return: True if the expected amount has been received, False otherwise.
        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            amount_received = self.rpc_connection.getreceivedbyaddress(address, min_confirmations)
            logger.info(f"Amount received at address '{address}': {amount_received} PEPE.")
            return amount_received >= expected_amount
        except JSONRPCException as e:
            logger.error(f"Failed to check payment for address '{address}': {e}")
            raise e

    # ------------------------- Utility Methods -------------------------

    def get_account_info(self) -> Dict:
        """
        Get general information about the account.

        :return: Account information.
        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            balance = self.get_balance()
            addresses = self.list_addresses()
            info = {
                'account_name': self.account_name,
                'balance': balance,
                'addresses': addresses
            }
            logger.info(f"Retrieved account info for '{self.account_name}'.")
            return info
        except Exception as e:
            logger.error(f"Failed to get account info for '{self.account_name}': {e}")
            raise e

    def validate_address(self, address: str) -> Dict:
        """
        Validate a Pepecoin address and retrieve its information.

        :param address: Address to validate.
        :return: Validation information.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            address_info = self.rpc_connection.validateaddress(address)
            logger.info(f"Validated address '{address}'.")
            return address_info
        except JSONRPCException as e:
            logger.error(f"Failed to validate address '{address}': {e}")
            raise e

    # ------------------------- Account Management -------------------------

    def get_received_by_account(self, min_confirmations: int = 1) -> float:
        """
        Get the total amount received by this account.

        :param min_confirmations: Minimum number of confirmations.
        :return: Total amount received.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            amount_received = self.rpc_connection.getreceivedbyaccount(self.account_name, min_confirmations)
            logger.info(f"Total amount received by account '{self.account_name}': {amount_received} PEPE.")
            return amount_received
        except JSONRPCException as e:
            logger.error(f"Failed to get received amount for account '{self.account_name}': {e}")
            raise e

    def list_transactions_by_account(
        self,
        count: int = 10,
        skip: int = 0
    ) -> List[Dict]:
        """
        List transactions for this account.

        :param count: Number of transactions to retrieve.
        :param skip: Number of transactions to skip.
        :return: List of transaction details.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            transactions = self.rpc_connection.listtransactions(self.account_name, count, skip)
            logger.info(f"Retrieved {len(transactions)} transactions for account '{self.account_name}'.")
            return transactions
        except JSONRPCException as e:
            logger.error(f"Failed to list transactions for account '{self.account_name}': {e}")
            raise e
