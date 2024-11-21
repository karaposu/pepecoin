#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Variables
PEPECOIN_VERSION="1.0.1"  # Latest version
PEPECOIN_DMG="pepecoin-${PEPECOIN_VERSION}-osx-unsigned.dmg"
PEPECOIN_URL="https://github.com/pepecoinppc/pepecoin/releases/download/v${PEPECOIN_VERSION}/${PEPECOIN_DMG}"
INSTALL_DIR="$HOME/pepecoin"
DATA_DIR="$HOME/Library/Application Support/Pepecoin"
RPC_PORT=33873  # Default RPC port for Pepecoin

echo "Starting Pepecoin node setup on macOS..."

# Prompt user for RPC credentials
read -p "Enter a username for RPC authentication: " RPC_USER
read -s -p "Enter a strong password for RPC authentication: " RPC_PASSWORD
echo

# Create install directory
mkdir -p "$INSTALL_DIR"

# Check if DMG file already exists
if [ -f "$INSTALL_DIR/$PEPECOIN_DMG" ]; then
    echo "Pepecoin Core DMG already exists at $INSTALL_DIR/$PEPECOIN_DMG."
    read -p "Do you want to redownload and replace it? (y/n): " REDOWNLOAD_DMG
    if [ "$REDOWNLOAD_DMG" = "y" ] || [ "$REDOWNLOAD_DMG" = "Y" ]; then
        echo "Redownloading Pepecoin Core DMG..."
        curl -L -o "$INSTALL_DIR/$PEPECOIN_DMG" "$PEPECOIN_URL"
    else
        echo "Using existing Pepecoin Core DMG."
    fi
else
    # Download Pepecoin Core DMG
    echo "Downloading Pepecoin Core DMG..."
    curl -L -o "$INSTALL_DIR/$PEPECOIN_DMG" "$PEPECOIN_URL"
fi

# Check if Pepecoin-Qt.app is already installed
if [ -d "/Applications/Pepecoin-Qt.app" ]; then
    echo "Pepecoin-Qt.app is already installed in /Applications."
    read -p "Do you want to redownload and replace it? (y/n): " REDOWNLOAD_APP
    if [ "$REDOWNLOAD_APP" = "y" ] || [ "$REDOWNLOAD_APP" = "Y" ]; then
        INSTALL_PEPECOIN_QT=true
    else
        INSTALL_PEPECOIN_QT=false
        echo "Skipping installation of Pepecoin-Qt.app since it already exists."
    fi
else
    INSTALL_PEPECOIN_QT=true
fi

if [ "$INSTALL_PEPECOIN_QT" = true ]; then
    # Mount the DMG
    echo "Mounting DMG..."
    hdiutil attach "$INSTALL_DIR/$PEPECOIN_DMG" -mountpoint /Volumes/Pepecoin

    # Copy Pepecoin Core application to Applications folder
    echo "Copying Pepecoin Core to Applications folder..."
    cp -r /Volumes/Pepecoin/Pepecoin-Qt.app /Applications/

    # Unmount the DMG
    echo "Unmounting DMG..."
    hdiutil detach /Volumes/Pepecoin
fi

# Copy pepecoind and pepecoin-cli to install directory
echo "Copying pepecoind and pepecoin-cli to $INSTALL_DIR/bin..."
mkdir -p "$INSTALL_DIR/bin"
if [ -f "/Applications/Pepecoin-Qt.app/Contents/MacOS/pepecoind" ] && [ -f "/Applications/Pepecoin-Qt.app/Contents/MacOS/pepecoin-cli" ]; then
    cp /Applications/Pepecoin-Qt.app/Contents/MacOS/pepecoind "$INSTALL_DIR/bin/"
    cp /Applications/Pepecoin-Qt.app/Contents/MacOS/pepecoin-cli "$INSTALL_DIR/bin/"
    chmod +x "$INSTALL_DIR/bin/pepecoind" "$INSTALL_DIR/bin/pepecoin-cli"
else
    echo "pepecoind and pepecoin-cli not found in Pepecoin-Qt.app."
    echo "Please ensure that the Pepecoin Core installation includes these files."
    exit 1
fi

# Add Pepecoin binaries to PATH
echo "Adding Pepecoin binaries to PATH..."
export PATH="$INSTALL_DIR/bin:$PATH"
echo 'export PATH="'$INSTALL_DIR'/bin:$PATH"' >> "$HOME/.bash_profile"
echo 'export PATH="'$INSTALL_DIR'/bin:$PATH"' >> "$HOME/.zshrc"

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

echo "Pepecoin node setup completed successfully on macOS."


# D0r!any3s!l24.