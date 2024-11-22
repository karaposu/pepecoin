# example_usage.py

from pepecoin_rpc import PepecoinRPC
from dotenv import load_dotenv
import os
load_dotenv()

rpc_user = os.getenv("RPC_USER")
rpc_password = os.getenv("RPC_PASSWORD")

# Initialize the Pepecoin RPC client
pepecoin_rpc = PepecoinRPC(rpc_user, rpc_password)

# Generate a new address
new_address = pepecoin_rpc.generate_new_address(label="order_123")
print(f"New Address: {new_address}")

# Get the wallet balance
balance = pepecoin_rpc.get_balance()
print(f"Wallet Balance: {balance} PEPE")
