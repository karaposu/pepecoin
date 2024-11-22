# pepecoin_rpc.py

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

class PepecoinRPC:
    def __init__(self, rpc_user, rpc_password, host='127.0.0.1', port=33873):
        self.rpc_user = rpc_user
        self.rpc_password = rpc_password
        self.host = host
        self.port = port
        self.rpc_connection = self.connect_to_node()

    def connect_to_node(self):
        rpc_url = f"http://{self.rpc_user}:{self.rpc_password}@{self.host}:{self.port}"
        return AuthServiceProxy(rpc_url)

    def generate_new_address(self, label=""):
        try:
            address = self.rpc_connection.getnewaddress(label)
            return address
        except JSONRPCException as e:
            print(f"Error generating new address: {e}")
            return None

    def get_received_by_address(self, address, minconf=1):
        try:
            amount = self.rpc_connection.getreceivedbyaddress(address, minconf)
            return amount
        except JSONRPCException as e:
            print(f"Error getting received amount: {e}")
            return None

    def get_transaction(self, txid):
        try:
            transaction = self.rpc_connection.gettransaction(txid)
            return transaction
        except JSONRPCException as e:
            print(f"Error getting transaction: {e}")
            return None

    def list_transactions(self, count=10, skip=0, include_watchonly=False):
        try:
            transactions = self.rpc_connection.listtransactions("*", count, skip, include_watchonly)
            return transactions
        except JSONRPCException as e:
            print(f"Error listing transactions: {e}")
            return None

    def get_blockchain_info(self):
        try:
            info = self.rpc_connection.getblockchaininfo()
            return info
        except JSONRPCException as e:
            print(f"Error getting blockchain info: {e}")
            return None

    def get_balance(self, minconf=1, include_watchonly=False):
        try:
            balance = self.rpc_connection.getbalance("*", minconf, include_watchonly)
            return balance
        except JSONRPCException as e:
            print(f"Error getting balance: {e}")
            return None

    def unlock_wallet(self, passphrase, timeout):
        try:
            self.rpc_connection.walletpassphrase(passphrase, timeout)
            print("Wallet unlocked successfully.")
        except JSONRPCException as e:
            print(f"Error unlocking wallet: {e}")

    def lock_wallet(self):
        try:
            self.rpc_connection.walletlock()
            print("Wallet locked successfully.")
        except JSONRPCException as e:
            print(f"Error locking wallet: {e}")
