#!/usr/bin/env python3

import subprocess
import json
import time

# Path to pepecoin-cli
PEPECOIN_CLI = 'pepecoin-cli'  # Assumes pepecoin-cli is in PATH


def get_blockchain_info():
    try:
        # Execute the pepecoin-cli getblockchaininfo command
        result = subprocess.run([PEPECOIN_CLI, 'getblockchaininfo'], capture_output=True, text=True)

        # Check for errors
        if result.returncode != 0:
            print("Error executing pepecoin-cli:", result.stderr.strip())
            return None

        # Parse the JSON output
        info = json.loads(result.stdout)
        return info
    except Exception as e:
        print("Exception occurred:", str(e))
        return None


def monitor_node():
    while True:
        info = get_blockchain_info()
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

        # Wait for a specified interval before checking again
        time.sleep(60)  # Check every 60 seconds


if __name__ == '__main__':
    monitor_node()
