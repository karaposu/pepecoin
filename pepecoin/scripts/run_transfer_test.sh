#!/usr/bin/env bash

# Exit on errors
set -e

EPECOIN_CONF="$HOME/.pepecoin/pepecoin.conf"

# --- Read RPC credentials from ~/.pepecoin/pepecoin.conf ---
if [ ! -f "$PEPECOIN_CONF" ]; then
    echo "Pepecoin config not found at: $PEPECOIN_CONF"
    exit 1
fi

# Parse the file for rpcuser and rpcpassword
RPC_USER=$(grep '^rpcuser=' "$PEPECOIN_CONF" | cut -d '=' -f 2-)
RPC_PASSWORD=$(grep '^rpcpassword=' "$PEPECOIN_CONF" | cut -d '=' -f 2-)

if [ -z "$RPC_USER" ] || [ -z "$RPC_PASSWORD" ]; then
    echo "Could not find rpcuser or rpcpassword in $PEPECOIN_CONF"
    exit 1
fi

# Export them so they’re available in the current shell environment
export RPC_USER
export RPC_PASSWORD
echo "Exported RPC_USER and RPC_PASSWORD from $PEPECOIN_CONF"

# Find the active Python's site-packages directory
SITE_PACKAGES=$(python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])")

if [ -z "$SITE_PACKAGES" ]; then
    echo "Could not determine site-packages directory."
    exit 1
fi

echo "Site-packages directory found at: $SITE_PACKAGES"

# Change to the site-packages directory
cd "$SITE_PACKAGES"

# Run the test module
echo "Running pepecoin.test_transfer..."
python -m pepecoin.test_transfer
