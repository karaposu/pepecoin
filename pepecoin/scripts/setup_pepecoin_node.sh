#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e


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


INSTALL_DIR="$HOME/pepecoin"
DATA_DIR="$HOME/.pepecoin"
RPC_PORT=33873  # Default RPC port for Pepecoin
PEPECOIN_CLI="$INSTALL_DIR/bin/pepecoin-cli"
PEPECOIN_DAEMON="$INSTALL_DIR/bin/pepecoind"
PEPECOIN_URL="https://github.com/pepecoinppc/pepecoin/releases/download/v${PEPECOIN_VERSION}/${PEPECOIN_FILE}"

echo "Starting Pepecoin node setup..."

# Check if pepecoin is already running
if [ -x "$PEPECOIN_CLI" ]; then
    if $PEPECOIN_CLI getblockchaininfo > /dev/null 2>&1; then
        echo "Pepecoin Core is already running."
        read -p "Pepecoin Core must be stopped before continuing. Stop now? (yes/no): " STOP_NOW
        if [ "$STOP_NOW" == "yes" ]; then
            echo "Stopping Pepecoin Core..."
            $PEPECOIN_CLI stop
            /bin/sleep 5
            if $PEPECOIN_CLI getblockchaininfo > /dev/null 2>&1; then
                echo "Pepecoin Core is still running. Please stop it manually and rerun the setup."
                exit 1
            fi
        else
            echo "Cannot continue while Pepecoin Core is running. Exiting."
            exit 1
        fi
    fi
fi

# Prompt user for RPC credentials
read -p "Enter a username for RPC authentication: " RPC_USER

# Prompt for password twice and check if they match
while true; do
    read -s -p "Enter a strong password for RPC authentication: " RPC_PASSWORD
    echo
    read -s -p "Confirm the password: " RPC_PASSWORD_CONFIRM
    echo
    if [ "$RPC_PASSWORD" == "$RPC_PASSWORD_CONFIRM" ]; then
        echo "Passwords match. Proceding..."
        break
    else
        echo "Passwords do not match. Please try again."
    fi
done


export RPC_USER="$RPC_USER"
export RPC_PASSWORD="$RPC_PASSWORD"
echo "RPC_USER and RPC_PASSWORD have been set to env for this session only."
echo "This is done so you can run the test script with same configuration."

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
export PATH="$INSTALL_DIR/bin:$PATH"
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi
echo "export PATH=\"$INSTALL_DIR/bin:\$PATH\"" >> "$SHELL_RC"

echo "Starting Pepecoin daemon..."
"$PEPECOIN_DAEMON" -daemon
echo "Pepecoin server starting"

# Wait for the daemon to fully start. Check repeatedly if it's ready.
ATTEMPTS=0
MAX_ATTEMPTS=12
while true; do
    /bin/sleep 5
    if OUTPUT=$("$PEPECOIN_CLI" getblockchaininfo 2>&1); then
        echo "Pepecoin daemon started successfully."
        break
    else
        # Check for "error code: -28" (Loading block index...)
        if echo "$OUTPUT" | grep -q 'error code: -28'; then
            echo "Pepecoin is still loading block index. Retrying..."
            ATTEMPTS=$((ATTEMPTS+1))
            if [ $ATTEMPTS -ge $MAX_ATTEMPTS ]; then
                echo "Daemon did not become ready within the allotted time."
                echo "Last output was:"
                echo "$OUTPUT"
                exit 1
            fi
        else
            echo "Failed to start Pepecoin daemon."
            echo "Output was:"
            echo "$OUTPUT"
            exit 1
        fi
    fi
done


echo "Pepecoin node setup completed successfully."


# Find pepecoin-cli path and add it to PATH if found
PEPECOIN_CLI_PATH=$(find / -type f -name pepecoin-cli 2>/dev/null | head -n 1)
if [ -n "$PEPECOIN_CLI_PATH" ]; then
    PEPECOIN_DIR=$(dirname "$PEPECOIN_CLI_PATH")
    # Add to PATH for current session
    export PATH="$PEPECOIN_DIR:$PATH"
    # Add to shell RC file for future sessions
    echo "export PATH=\"$PEPECOIN_DIR:\$PATH\"" >> "$SHELL_RC"
    echo "Found pepecoin-cli at $PEPECOIN_CLI_PATH and added it to PATH."
else
    echo "pepecoin-cli not found by global search. It's likely in $INSTALL_DIR/bin already."
fi

echo "To test essential capabilities with the help of pepecoin package please run: "
echo "pepecoin-test"
