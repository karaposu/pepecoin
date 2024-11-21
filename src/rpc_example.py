# example_usage.py

from pepecoin_rpc import PepecoinRPC

# Replace with your actual RPC credentials
rpc_user = "your_rpc_username"
rpc_password = "your_rpc_password"

# Initialize the Pepecoin RPC client
pepecoin_rpc = PepecoinRPC(rpc_user, rpc_password)

# Generate a new address
new_address = pepecoin_rpc.generate_new_address(label="order_123")
print(f"New Address: {new_address}")

# Get the wallet balance
balance = pepecoin_rpc.get_balance()
print(f"Wallet Balance: {balance} PEPE")
