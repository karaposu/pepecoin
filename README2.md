# Pepecoin Python Client

A Python client library for interacting with a Pepecoin node via RPC. The `Pepecoin` class provides a simplified interface for wallet management, address generation, balance checking, payment verification, node connection checking, wallet locking/unlocking, and mass transferring funds.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Dependencies](#dependencies)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setting Up the Pepecoin Node](#setting-up-the-pepecoin-node)
- [Usage Examples](#usage-examples)
  - [Initialize the Pepecoin Client](#initialize-the-pepecoin-client)
  - [Check Node Connection](#check-node-connection)
  - [Create a New Wallet](#create-a-new-wallet)
  - [Generate a New Address](#generate-a-new-address)
  - [Check Wallet Balance](#check-wallet-balance)
  - [Check for Payments](#check-for-payments)
  - [Lock and Unlock Wallet](#lock-and-unlock-wallet)
  - [Mass Transfer Funds](#mass-transfer-funds)
- [API Reference](#api-reference)
  - [`__init__`](#__init__)
  - [`init_rpc`](#init_rpc)
  - [`check_node_connection`](#check_node_connection)
  - [`create_new_wallet`](#create_new_wallet)
  - [`get_wallet_rpc`](#get_wallet_rpc)
  - [`lock_wallet`](#lock_wallet)
  - [`unlock_wallet`](#unlock_wallet)
  - [`generate_new_address`](#generate_new_address)
  - [`check_balance`](#check_balance)
  - [`check_payment`](#check_payment)
  - [`mass_transfer`](#mass_transfer)
- [Security Considerations](#security-considerations)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Simplified RPC Connection**: Easily connect to a Pepecoin node using RPC.
- **Wallet Management**: Create, encrypt, lock, and unlock wallets.
- **Address Generation**: Generate new Pepecoin addresses with optional labels.
- **Balance Checking**: Check the balance of wallets.
- **Payment Verification**: Verify if payments have been received at specific addresses.
- **Mass Transfer**: Transfer funds from multiple wallets to a single address.
- **Node Connection Checking**: Verify if the Pepecoin node is connected and reachable.

---

## Installation

Install the package via `pip`:

```bash
pip install python-bitcoinrpc
```

---

## Dependencies

- **Python 3.6+**
- **[python-bitcoinrpc](https://github.com/jgarzik/python-bitcoinrpc)**: For RPC communication with the Pepecoin node.

---

## Getting Started

### Prerequisites

- **Running Pepecoin Node**: You must have a Pepecoin node running with RPC enabled.
- **RPC Credentials**: Set up `rpcuser` and `rpcpassword` in your `pepecoin.conf` file.
- **Python Environment**: Ensure you have Python 3.6 or higher installed.

### Setting Up the Pepecoin Node

1. **Install Pepecoin Core**: Follow the instructions to install the Pepecoin Core software.
2. **Configure the Node**:

   Add the following lines to your `pepecoin.conf` file:

   ```conf
   server=1
   rpcuser=your_rpc_username
   rpcpassword=your_rpc_password
   rpcallowip=127.0.0.1
   rpcport=29373
   ```

3. **Start the Node**:

   ```bash
   pepecoind -daemon
   ```

---

## Usage Examples

### Initialize the Pepecoin Client

```python
from pepecoin import Pepecoin

# Initialize the Pepecoin client
pepecoin = Pepecoin(
    rpc_user="your_rpc_username",
    rpc_password="your_rpc_password",
    host="127.0.0.1",
    port=29373,
    wallet_name="merchant_wallet"
)
```

### Check Node Connection

```python
if pepecoin.check_node_connection():
    print("Node is connected.")
else:
    print("Node is not connected.")
```

### Create a New Wallet

```python
wallet_created = pepecoin.create_new_wallet(
    wallet_name="merchant_wallet",
    passphrase="secure_passphrase"
)
if wallet_created:
    print("Wallet created successfully.")
else:
    print("Failed to create wallet.")
```

### Generate a New Address

```python
payment_address = pepecoin.generate_new_address(label="order_12345")
print(f"Payment Address: {payment_address}")
```

### Check Wallet Balance

```python
balance = pepecoin.check_balance()
print(f"Wallet Balance: {balance} PEPE")
```

### Check for Payments

```python
payment_received = pepecoin.check_payment(
    address=payment_address,
    expected_amount=10.0
)
if payment_received:
    print("Payment received.")
else:
    print("Payment not yet received.")
```

### Lock and Unlock Wallet

```python
# Unlock the wallet
pepecoin.unlock_wallet(
    wallet_name="merchant_wallet",
    passphrase="secure_passphrase",
    timeout=60  # Unlock for 60 seconds
)

# Lock the wallet
pepecoin.lock_wallet(wallet_name="merchant_wallet")
```

### Mass Transfer Funds

```python
from_wallets = ["wallet1", "wallet2"]
passphrases = ["passphrase1", "passphrase2"]
to_address = "PMainWalletAddress1234567890"

tx_ids = pepecoin.mass_transfer(
    from_wallets=from_wallets,
    to_address=to_address,
    passphrases=passphrases
)
print(f"Mass transfer transaction IDs: {tx_ids}")
```

---

## API Reference

### `__init__`

Initialize the Pepecoin RPC connection.

```python
def __init__(
    self,
    rpc_user: str,
    rpc_password: str,
    host: str = '127.0.0.1',
    port: int = 29373,
    wallet_name: Optional[str] = None
) -> None:
```

- **Parameters**:
  - `rpc_user`: RPC username.
  - `rpc_password`: RPC password.
  - `host`: Host where the Pepecoin node is running.
  - `port`: RPC port of the Pepecoin node.
  - `wallet_name`: Name of the wallet to interact with (optional).

### `init_rpc`

Initialize the RPC connection to the Pepecoin node.

```python
def init_rpc(self) -> AuthServiceProxy:
```

- **Returns**: `AuthServiceProxy` object.

### `check_node_connection`

Check if the node is connected and reachable.

```python
def check_node_connection(self) -> bool:
```

- **Returns**: `True` if connected, `False` otherwise.

### `create_new_wallet`

Create a new wallet.

```python
def create_new_wallet(
    self,
    wallet_name: str,
    passphrase: str = None,
    disable_private_keys: bool = False
) -> bool:
```

- **Parameters**:
  - `wallet_name`: Name of the new wallet.
  - `passphrase`: Passphrase to encrypt the wallet (optional).
  - `disable_private_keys`: If `True`, the wallet will not contain private keys.
- **Returns**: `True` if wallet was created successfully, `False` otherwise.

### `get_wallet_rpc`

Get an RPC connection for a specific wallet.

```python
def get_wallet_rpc(self, wallet_name: str) -> AuthServiceProxy:
```

- **Parameters**:
  - `wallet_name`: Name of the wallet.
- **Returns**: `AuthServiceProxy` object connected to the wallet.

### `lock_wallet`

Lock the specified wallet.

```python
def lock_wallet(self, wallet_name: Optional[str] = None) -> None:
```

- **Parameters**:
  - `wallet_name`: Name of the wallet to lock. If `None`, uses the default wallet.

### `unlock_wallet`

Unlock the specified wallet.

```python
def unlock_wallet(
    self,
    wallet_name: Optional[str],
    passphrase: str,
    timeout: int = 60
) -> None:
```

- **Parameters**:
  - `wallet_name`: Name of the wallet to unlock.
  - `passphrase`: Passphrase of the wallet.
  - `timeout`: Time in seconds for which the wallet remains unlocked.

### `generate_new_address`

Generate a new Pepecoin address.

```python
def generate_new_address(self, label: str = None) -> str:
```

- **Parameters**:
  - `label`: Label to associate with the new address (optional).
- **Returns**: The new Pepecoin address.

### `check_balance`

Check the balance of the specified wallet.

```python
def check_balance(self, wallet_name: Optional[str] = None) -> float:
```

- **Parameters**:
  - `wallet_name`: Name of the wallet to check balance for. If `None`, uses the default wallet.
- **Returns**: The balance of the wallet.

### `check_payment`

Check if the expected amount has been received at the specified address.

```python
def check_payment(
    self,
    address: str,
    expected_amount: float,
    min_confirmations: int = 1
) -> bool:
```

- **Parameters**:
  - `address`: The Pepecoin address to check.
  - `expected_amount`: The expected amount to be received.
  - `min_confirmations`: Minimum number of confirmations required.
- **Returns**: `True` if the expected amount has been received, `False` otherwise.

### `mass_transfer`

Transfer funds from multiple wallets to a target address.

```python
def mass_transfer(
    self,
    from_wallets: List[str],
    to_address: str,
    passphrases: Optional[List[str]] = None
) -> List[str]:
```

- **Parameters**:
  - `from_wallets`: List of wallet names to transfer from.
  - `to_address`: The target Pepecoin address to transfer funds to.
  - `passphrases`: List of passphrases for the wallets (if encrypted).
- **Returns**: List of transaction IDs.

---

## Security Considerations

- **Passphrases**: Never hardcode passphrases in your code. Use secure methods to store and retrieve them (e.g., environment variables, secure key management systems).
- **RPC Credentials**: Protect your RPC credentials. Do not expose them in logs or version control.
- **Wallet Encryption**: Always encrypt wallets that hold real funds.
- **Node Security**: Ensure your Pepecoin node is secure, with proper firewall settings and access controls.
- **SSL/TLS Encryption**: Consider using SSL/TLS for RPC communications.

---

## License

This project is licensed under the MIT License.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

---

## Acknowledgments

- [python-bitcoinrpc](https://github.com/jgarzik/python-bitcoinrpc) for providing the RPC client library.

---

**Note**: This client library is provided as-is. Use it at your own risk. Ensure that you understand the security implications of interacting with cryptocurrency nodes and wallets.