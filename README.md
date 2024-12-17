

This repository is an independent project and is not affiliated with the official Pepecoin team (Yet this project uses the same pepecoin). For the official Pepecoin repository, please visit [Pepecoin Core](https://github.com/pepecoinppc/pepecoin).

(Please with third party crypto libraries (like this one) always read the source code before running. Make it a habit)


<h1 align="center">
<img src="https://raw.githubusercontent.com/karaposu/pepecoin/refs/heads/main/pepe_logo.png" alt="Pepecoin" width="300"/>
<br/><br/>
Pepecoin(₱) Python Client 
</h1>

Pepecoin Python Client is a python client library for easily interacting with a Pepecoin node (via RPC) and developing cool applications.

If you want to check out a "Pepecoin Payment Gateway" example, check out this link: [Pepecoin FastAPI Payment Gateway](https://github.com/karaposu/pepecoin-fastapi-payment-gateway).

The `Pepecoin` class provides a simplified interface for wallet management, address generation, balance checking, payment verification, node connection checking, wallet locking/unlocking, and mass transferring funds.

---

## Features

- **Simplified RPC Connection**: Easily connect to a Pepecoin node using RPC.
- **Account Management**: Create and manage multiple "accounts" within the single wallet (a legacy feature of the Pepecoin node). Accounts allow you to logically organize funds under different labels.
- **Address Generation**: Generate new Pepecoin addresses with optional labels.
- **Balance Checking**: Check the balance of accounts.
- **Payment Verification**: Verify that a certain amount of PEP was received at a specific address
- **Mass Transfer**: Transfer funds from multiple accounts to a single address for consolidation or payouts.
- **Node Connection Checking**: Quickly verify that the Pepecoin node is up and reachable via RPC.
-  **Wallet Locking/Unlocking**: Encrypt the single wallet (where all accounts live). Lock and unlock the wallet for a specified duration to allow outgoing transactions.

---

## Installation

Install the package via `pip`:

```bash
pip install pepecoin

# to install latest unstable version:
# pip install -e git+https://github.com/karaposu/pepecoin.git#egg=pepecoin
```


---

## Step by Step Pepecoin Node Setup Guide

###  0. Install Python 3.11 [Optional, Linux Only]

- **Linux**: copy and run below command
``` 
curl -fsSL https://raw.githubusercontent.com/karaposu/pepecoin/refs/heads/main/pepecoin/scripts/virgin_vm.sh | bash

```

###  0. Prerequisites for Mac Users 

- **MacOS**: MacOS version must be at least 15
- **Xcode**: Download Xcode and Xcode command line tools
- **OpenSSL 1.1**: We need openSSL 1.1 to build from source. 


###  1. Install pepecoin package

``` 
pip install pepecoin
```

###  2. Run the setup script

This script will clone official pepecoin core and:
1. Prompts you to create rpc_user and rpc_password 
2. Download compiled binaries
3. Create pepecoin.conf
4. Add Pepecoin binaries to PATH
5. Start Pepecoin daemon
6. Verify the daemon is indeed running 

(rpc_user and password can be found in ~/.pepecoin/pepecoin.conf) 



- **For Linux**
  ```bash
  pepecoin-setup
  
  # dont forget to run
  
  source ~/.bashrc
  ```

- **For MacOS(will be ready soon)**

Offical repo installation does not support pepecoin-cli for MacOS. So I patched it and made it work. But use it only for development. 
  ```bash
  pepecoin-setup-macos
  # this will build pepecoin binaries using openssl 1.1
  ```

###  3. Run the test script

- **For Linux**
  ```bash
  pepecoin-test
  ```

This will test RPC connection as well as wallet creation
synch feature and some other essentials. 


###  4. Run the coin transfer test script


- **For Linux**
  ```bash
  pepecoin-transfer-test


  # if you want to check if destination account indeed got the pepe run: 
  
  pepecoin-cli getreceivedbyaddress "destination_address_here"

  # if you want to check the remaining balance of the source account run:
  
  pepecoin-cli getbalance "source_address_here"

  ```


- This will test account logic. You will need to send some coin to source_account. (You may buy pepecoin from Xeggex.com) 
- Rerun to see if coin is delivered. 
- If the coin is delivered, script will send 0.1 pepecoin to destination address. 



## Simple Troubleshooting

Make sure pepecoin node is running by running :

`pepecoind -daemon`

Run `pepecoin-cli getblockchaininfo`  and if you dont see a json output go to installation_troubleshooting.md 



## Understanding the Limitations of Pepecoin Blockchain

1. Pepecoin is based on an older version of Bitcoin Core (likely around 0.10.x), which does not support the createwallet RPC method or multi-wallet functionality introduced in Bitcoin Core 0.17.0.

2. Single Wallet System: In this version, the node operates with a single wallet (wallet.dat) located in the data directory. There is no native support for managing multiple wallets via RPC calls. 

3. To simulate wallet logic "accounts" are used. Accounts allow you to partition your wallet into multiple logical sections, effectively simulating multiple wallets.

4.  How Accounts Work can be summed like this: 
  - Separate Balances: Each account maintains its own balance, separate from other accounts.
  - Address Management: You can generate addresses associated with specific accounts.
  - Transaction Tracking: Transactions can be attributed to specific accounts.
  - All accounts share the same underlying wallet file. There is no way to encrypt accounts individually via RPC. Wallet-level encryption affects all accounts.

5. "accounts" are essentially labels for your addresses that share a single wallet.dat. So the act of creating a new account is conceptually just getting an Account instance tied to a name (label). If the account doesn't exist yet, Pepecoin implicitly creates it for you when you first reference it.



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
    port=33873,
    wallet_name="merchant_wallet"
)
```

### Check Node Connection

```
if pepecoin.check_node_connection():
    print("Node is connected.")
else:
    print("Node is not connected.")
```

### Create a New Account 
```
from pepecoin import Pepecoin

# Initialize the Pepecoin client
pepecoin = Pepecoin(
    rpc_user="pepe_user",
    rpc_password="pepe_pass",
    host="127.0.0.1",
    port=33873
)

# Creating (or retrieving) an account named "my_new_account"
my_new_account = pepecoin.get_account("my_new_account")

# Optionally, generate an address for that account to begin using it
new_address = my_new_account.generate_address()
print(f"New Address for 'my_new_account': {new_address}")
```

Note: This won't create a standalone wallet file. Instead, it creates or references a label inside the single Pepecoin wallet.


### Generate a New Address

You can generate a new address for a specific account. Each address is part of the single wallet but is logically grouped under your chosen "account" label.

```
# If you already have an Account instance
my_account = pepecoin.get_account("my_new_account")

# Generate a new address within this account
new_address = my_account.generate_address()
print(f"New Address: {new_address}")

# Or generate a new address without specifying an account (defaults to your main wallet account)
default_address = pepecoin.generate_new_address()
print(f"New Default Account Address: {default_address}")
```


### Check Account Balance



```
# Get an Account instance
my_account = pepecoin.get_account("my_new_account")

# Retrieve the balance
balance = my_account.get_balance()
print(f"Balance for 'my_new_account': {balance} PEPE")

# Or directly from the Pepecoin instance (if you prefer an older naming convention)
account_balance = pepecoin.get_balance(account="my_new_account")
print(f"Balance for 'my_new_account': {account_balance} PEPE")
```



### Check Address Balance

To confirm if you've received a specific payment (for instance, 1.0 PEPE with at least 1 confirmation) at a given address:


```
# Suppose you have an address
address = "PcLbnQ6w3rxQPU..."
address_balance = pepecoin.get_balance_of_address(address)
print(f"Balance for address {address}: {address_balance} PEPE")
```


### Check for Payments

```
# Let's say you previously generated an address for your merchant account
my_account = pepecoin.get_account("merchant_account")
watch_address = my_account.generate_address()

# Wait for incoming payment, then check
expected_amount = 1.0  # PEPE
payment_received = my_account.check_payment(watch_address, expected_amount, min_confirmations=1)

if payment_received:
    print("Payment has arrived!")
else:
    print("No payment yet, or not enough confirmations.")
```

For robust payment checking, you might poll this method in your code (e.g., a cron job or a background task) until payment_received is True.

### Lock and Unlock Account
Wallet encryption in older Pepecoin (Bitcoin-Core-like) systems is at the wallet level, not the account level. So locking or unlocking applies to the entire wallet (all accounts).

```
# Unlock the wallet for 60 seconds
try:
    pepecoin.rpc_connection.walletpassphrase("my_w0rldClass#Passphrase", 60)
    print("Wallet unlocked successfully!")
except Exception as e:
    print(f"Error unlocking wallet: {e}")

# ... do your sending operations, e.g. send_from, move, etc. ...

# Lock the wallet again
try:
    pepecoin.rpc_connection.walletlock()
    print("Wallet locked successfully!")
except Exception as e:
    print(f"Error locking wallet: {e}")
```





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