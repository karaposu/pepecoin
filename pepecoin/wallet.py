# wallet.py

from typing import List, Dict, Optional
from pepecoin import Pepecoin
from bitcoinrpc.authproxy import JSONRPCException
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Wallet:
    def __init__(self, pepecoin_client: Pepecoin, wallet_name: str):
        """
        Initialize the Wallet instance.

        :param pepecoin_client: An instance of the Pepecoin class for RPC interactions.
        :param wallet_name: The name of the wallet to manage.
        """
        self.pepecoin = pepecoin_client
        self.wallet_name = wallet_name
        self.wallet_rpc = self.pepecoin.get_wallet_rpc(wallet_name)
        logger.debug(f"Initialized Wallet for '{self.wallet_name}'.")

    # ------------------------- Wallet Management -------------------------

    def lock_wallet(self) -> None:
        """
        Lock the wallet.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.pepecoin.lock_wallet(self.wallet_name)
            logger.info(f"Wallet '{self.wallet_name}' locked successfully.")
        except JSONRPCException as e:
            logger.error(f"Failed to lock wallet '{self.wallet_name}': {e}")
            raise e

    def unlock_wallet(self, passphrase: str, timeout: int = 60) -> None:
        """
        Unlock the wallet.

        :param passphrase: Wallet passphrase.
        :param timeout: Duration in seconds to keep the wallet unlocked.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.pepecoin.unlock_wallet(self.wallet_name, passphrase, timeout)
            logger.info(f"Wallet '{self.wallet_name}' unlocked successfully for {timeout} seconds.")
        except JSONRPCException as e:
            logger.error(f"Failed to unlock wallet '{self.wallet_name}': {e}")
            raise e

    # ------------------------- Address Management -------------------------

    def generate_address(self, label: Optional[str] = None) -> str:
        """
        Generate a new Pepecoin address with an optional label.

        :param label: Optional label for the address.
        :return: New Pepecoin address.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            address = self.pepecoin.generate_new_address(label)
            logger.info(f"Generated new address '{address}' with label '{label}'.")
            return address
        except JSONRPCException as e:
            logger.error(f"Failed to generate new address: {e}")
            raise e

    def list_addresses(self, label: Optional[str] = None) -> List[str]:
        """
        List all addresses, optionally filtered by label.

        :param label: Label to filter addresses.
        :return: List of addresses.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            if label:
                addresses = self.wallet_rpc.getaddressesbylabel(label)
                logger.info(f"Retrieved addresses with label '{label}': {addresses}")
            else:
                addresses = self.wallet_rpc.getaddressesbylabel("")
                logger.info(f"Retrieved all addresses: {addresses}")
            return addresses
        except JSONRPCException as e:
            logger.error(f"Failed to list addresses: {e}")
            raise e

    # ------------------------- Transaction Management -------------------------

    def list_transactions(self, count: int = 10, skip: int = 0, include_watchonly: bool = False) -> List[Dict]:
        """
        List recent transactions.

        :param count: Number of transactions to retrieve.
        :param skip: Number of transactions to skip.
        :param include_watchonly: Include watch-only addresses.
        :return: List of transaction details.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            transactions = self.wallet_rpc.listtransactions("*", count, skip, include_watchonly)
            logger.info(f"Retrieved {len(transactions)} transactions.")
            return transactions
        except JSONRPCException as e:
            logger.error(f"Failed to list transactions: {e}")
            raise e

    def send_to_address(self, address: str, amount: float, comment: str = "", comment_to: str = "") -> str:
        """
        Send PEPE to a specified address.

        :param address: Recipient's Pepecoin address.
        :param amount: Amount to send.
        :param comment: Optional comment.
        :param comment_to: Optional comment to the recipient.
        :return: Transaction ID.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            tx_id = self.wallet_rpc.sendtoaddress(address, amount, comment, comment_to)
            logger.info(f"Sent {amount} PEPE to '{address}'. Transaction ID: {tx_id}")
            return tx_id
        except JSONRPCException as e:
            logger.error(f"Failed to send to address '{address}': {e}")
            raise e

    def mass_transfer(self, recipients: Dict[str, float], fee: float = 0.0) -> List[str]:
        """
        Send funds to multiple recipients.

        :param recipients: Dictionary mapping addresses to amounts.
        :param fee: Transaction fee (optional, not used in this implementation).
        :return: List of transaction IDs.

        :raises JSONRPCException: If any RPC call fails.
        """
        tx_ids = []
        for address, amount in recipients.items():
            try:
                tx_id = self.send_to_address(address, amount)
                tx_ids.append(tx_id)
                logger.info(f"Mass transfer: Sent {amount} PEPE to '{address}'. Transaction ID: {tx_id}")
            except JSONRPCException as e:
                logger.error(f"Mass transfer failed for address '{address}': {e}")
                # Optionally, continue or abort based on requirements
                raise e
        return tx_ids

    # ------------------------- Key Management -------------------------

    def import_private_key(self, private_key: str, label: str = "", rescan: bool = True) -> None:
        """
        Import a private key into the wallet.

        :param private_key: The private key to import.
        :param label: Optional label for the address.
        :param rescan: Whether to rescan the blockchain.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.wallet_rpc.importprivkey(private_key, label, rescan)
            logger.info(f"Imported private key '{private_key}' with label '{label}'. Rescan: {rescan}")
        except JSONRPCException as e:
            logger.error(f"Failed to import private key: {e}")
            raise e

    def export_private_key(self, address: str) -> str:
        """
        Export the private key for a given address.

        :param address: The address to export the key for.
        :return: The private key.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            private_key = self.wallet_rpc.dumpprivkey(address)
            logger.info(f"Exported private key for address '{address}'.")
            return private_key
        except JSONRPCException as e:
            logger.error(f"Failed to export private key for address '{address}': {e}")
            raise e

    # ------------------------- Label Management -------------------------

    def set_label(self, address: str, label: str) -> None:
        """
        Assign a label to an address.

        :param address: The address to label.
        :param label: The label to assign.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.wallet_rpc.setlabel(address, label)
            logger.info(f"Set label '{label}' for address '{address}'.")
        except JSONRPCException as e:
            logger.error(f"Failed to set label for address '{address}': {e}")
            raise e

    def get_label(self, address: str) -> str:
        """
        Retrieve the label assigned to an address.

        :param address: The address to query.
        :return: The label of the address.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            address_info = self.wallet_rpc.validateaddress(address)
            label = address_info.get('label', '')
            logger.info(f"Retrieved label '{label}' for address '{address}'.")
            return label
        except JSONRPCException as e:
            logger.error(f"Failed to get label for address '{address}': {e}")
            raise e

    # ------------------------- Transaction Status -------------------------

    def get_transaction_status(self, txid: str) -> Dict:
        """
        Get the status of a specific transaction.

        :param txid: Transaction ID.
        :return: Transaction details.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            transaction = self.wallet_rpc.gettransaction(txid)
            logger.info(f"Retrieved status for transaction '{txid}'.")
            return transaction
        except JSONRPCException as e:
            logger.error(f"Failed to get transaction status for '{txid}': {e}")
            raise e

    # ------------------------- Backup and Restore -------------------------

    def backup_wallet(self, destination_path: str) -> None:
        """
        Backup the wallet to a specified location.

        :param destination_path: File path to save the backup.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.wallet_rpc.backupwallet(destination_path)
            logger.info(f"Wallet '{self.wallet_name}' backed up to '{destination_path}'.")
        except JSONRPCException as e:
            logger.error(f"Failed to backup wallet '{self.wallet_name}': {e}")
            raise e

    def restore_wallet(self, backup_path: str) -> None:
        """
        Restore the wallet from a backup file.

        :param backup_path: Path to the backup file.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            self.wallet_rpc.importwallet(backup_path)
            logger.info(f"Wallet '{self.wallet_name}' restored from backup '{backup_path}'.")
        except JSONRPCException as e:
            logger.error(f"Failed to restore wallet '{self.wallet_name}' from '{backup_path}': {e}")
            raise e

    # ------------------------- Address Validation -------------------------

    def validate_address(self, address: str) -> Dict:
        """
        Validate a Pepecoin address and retrieve its information.

        :param address: Address to validate.
        :return: Validation information including label.

        :raises JSONRPCException: If the RPC call fails.
        """
        try:
            address_info = self.wallet_rpc.validateaddress(address)
            logger.info(f"Validated address '{address}'.")
            return address_info
        except JSONRPCException as e:
            logger.error(f"Failed to validate address '{address}': {e}")
            raise e
