#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Variables
PEPECOIN_VERSION="1.0.1"  # Latest version

# Detect system architecture
ARCH=$(uname -m)
if [[ "$ARCH" == "x86_64" ]]; then
    PEPECOIN_FILE="pepecoin-${PEPECOIN_VERSION}-x86_64-linux-gnu.tar.gz"
elif [[ "$ARCH" == "aarch64" ]] || [[ "$ARCH" == "arm64" ]]; then
    PEPECOIN_FILE="pepecoin-${PEPECOIN_VERSION}-aarch64-linux-gnu.tar.gz"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

PEPECOIN_URL="https://github.com/pepecoinppc/pepecoin/releases/download/v${PEPECOIN_VERSION}/${PEPECOIN_FILE}"
INSTALL_DIR="$HOME/pepecoin"
DATA_DIR="$HOME/.pepecoin"
RPC_PORT=33873  # Default RPC port for Pepecoin

echo "Starting Pepecoin node setup..."

# Prompt user for RPC credentials
read -p "Enter a username for RPC authentication: " RPC_USER

# Prompt for password twice and check if they match
while true; do
    read -s -p "Enter a strong password for RPC authentication: " RPC_PASSWORD
    echo
    read -s -p "Confirm the password: " RPC_PASSWORD_CONFIRM
    echo
    if [ "$RPC_PASSWORD" == "$RPC_PASSWORD_CONFIRM" ]; then
        echo "Passwords match."
        break
    else
        echo "Passwords do not match. Please try again."
    fi
done

# Create install directory
mkdir -p "$INSTALL_DIR"

# Check if the binary archive already exists
if [ -f "$INSTALL_DIR/$PEPECOIN_FILE" ]; then
    echo "Pepecoin Core binary archive already exists at $INSTALL_DIR/$PEPECOIN_FILE."
    read -p "Do you want to redownload and replace it? (y/n): " REDOWNLOAD
    if [ "$REDOWNLOAD" = "y" ] || [ "$REDOWNLOAD" = "Y" ]; then
        echo "Redownloading Pepecoin Core binaries..."
        wget -O "$INSTALL_DIR/$PEPECOIN_FILE" "$PEPECOIN_URL"
    else
        echo "Using existing Pepecoin Core binary archive."
    fi
else
    # Download Pepecoin Core binaries
    echo "Downloading Pepecoin Core binaries..."
    wget -O "$INSTALL_DIR/$PEPECOIN_FILE" "$PEPECOIN_URL"
fi

# Check if Pepecoin binaries are already extracted
if [ -d "$INSTALL_DIR/bin" ]; then
    echo "Pepecoin Core binaries are already extracted in $INSTALL_DIR."
    read -p "Do you want to re-extract and replace them? (y/n): " REEXTRACT
    if [ "$REEXTRACT" = "y" ] || [ "$REEXTRACT" = "Y" ]; then
        echo "Re-extracting Pepecoin Core binaries..."
        tar -xzvf "$INSTALL_DIR/$PEPECOIN_FILE" -C "$INSTALL_DIR" --strip-components=1
    else
        echo "Using existing Pepecoin Core binaries."
    fi
else
    # Extract the binaries
    echo "Extracting Pepecoin Core binaries..."
    tar -xzvf "$INSTALL_DIR/$PEPECOIN_FILE" -C "$INSTALL_DIR" --strip-components=1
fi

# Create data directory
mkdir -p "$DATA_DIR"

# Create pepecoin.conf
echo "Creating pepecoin.conf..."
cat <<EOF > "$DATA_DIR/pepecoin.conf"
server=1
daemon=1
rpcuser=${RPC_USER}
rpcpassword=${RPC_PASSWORD}
rpcallowip=127.0.0.1
rpcport=${RPC_PORT}
txindex=1
EOF

echo "Configuration file created at $DATA_DIR/pepecoin.conf"

# Add Pepecoin binaries to PATH (optional)
echo "Adding Pepecoin binaries to PATH..."
export PATH="$INSTALL_DIR/bin:\$PATH"
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi
echo 'export PATH="'$INSTALL_DIR'/bin:$PATH"' >> "$SHELL_RC"

# Start Pepecoin daemon
echo "Starting Pepecoin daemon..."
"$INSTALL_DIR/bin/pepecoind" -daemon

# Wait a few seconds to ensure the daemon starts
sleep 5

# Check if the daemon is running
if "$INSTALL_DIR/bin/pepecoin-cli" getblockchaininfo > /dev/null 2>&1; then
    echo "Pepecoin daemon started successfully."
else
    echo "Failed to start Pepecoin daemon."
    exit 1
fi

echo "Pepecoin node setup completed successfully."
