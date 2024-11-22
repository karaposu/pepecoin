Synchronous vs. Asynchronous: The AuthServiceProxy class is synchronous. If you need asynchronous support, you might need to use an asynchronous RPC client or run synchronous code in a thread pool.







Certainly! Let's update your README to replace "placeholder" with the actual command that users can run to execute the setup script included in your Pepecoin package. This way, users will know exactly how to perform the automatic setup.

Given that you've included a CLI command `pepecoin-setup` in your package (as per previous discussions), we can instruct users to run this command.

Here's the corrected and updated README:

---

# Pepecoin Python Client

A Python client library for easily interacting with a Pepecoin node (via RPC) and developing cool applications.

If you want to check out a "Pepecoin Payment Gateway" example, check out this link: [Pepecoin FastAPI Payment Gateway](https://github.com/karaposu/pepecoin-fastapi-payment-gateway).

The `Pepecoin` class provides a simplified interface for wallet management, address generation, balance checking, payment verification, node connection checking, wallet locking/unlocking, and mass transferring funds.

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
pip install pepecoin
```

---

## Getting Started

### Prerequisites

- **Automatic Setup**: If you haven't gone through the official setup process, you can run the following command to start the installation automatically:

  ```bash
  pepecoin-setup
  ```

  This command will execute a bash script included in the Pepecoin package that follows the steps in the official [Pepecoin installation documentation](https://github.com/pepecoinppc/pepecoin/blob/master/INSTALL.md). Feel free to inspect the script before running it.

- **Running Pepecoin Node**: You must have a Pepecoin node running with RPC enabled (you can start it by running `pepecoind -daemon` from the terminal).

- **RPC Credentials**: Don't forget to add `RPC_USER` and `RPC_PASSWORD` in your `.env` file.

---

## Usage Examples

### Initialize the Pepecoin Client

```python
from pepecoin import Pepecoin
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the Pepecoin client
pepecoin = Pepecoin(
    rpc_user=os.environ.get("RPC_USER"),
    rpc_password=os.environ.get("RPC_PASSWORD"),
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

**Additional Notes:**

- Ensure that your `pepecoin` package includes the `pepecoin-setup` command in the `entry_points` of your `setup.py`:

  ```python
  entry_points={
      'console_scripts': [
          'pepecoin-setup=pepecoin.cli:setup_node',
          # ... other entry points ...
      ],
  },
  ```

- Make sure that your `pepecoin/cli.py` module includes the `setup_node` function that executes the setup script.

- The `pepecoin-setup` command may require elevated permissions to install system-wide dependencies. It's recommended to inspect the script before running it and to run it in a controlled environment.

---

Everything should now be clear and actionable for users. By providing the actual command `pepecoin-setup`, users can easily run the setup script included in your package.

**Feel free to reach out if you have any further questions or need additional assistance!**