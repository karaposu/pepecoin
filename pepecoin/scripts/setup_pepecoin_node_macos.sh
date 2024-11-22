#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Variables
PEPECOIN_VERSION="1.0.1"  # Latest version
INSTALL_DIR="$HOME/pepecoin"
DATA_DIR="$HOME/Library/Application Support/Pepecoin"
RPC_PORT=33873  # Default RPC port for Pepecoin

echo "Starting Pepecoin node setup on macOS..."

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

# Install Xcode command line tools if not installed
if ! xcode-select -p &>/dev/null; then
    echo "Installing Xcode command line tools..."
    xcode-select --install
    echo "Please complete the installation of Xcode command line tools and rerun this script."
    exit 1
fi

# Install Homebrew if not installed
if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Update Homebrew
echo "Updating Homebrew..."
brew update

# Install dependencies
echo "Installing dependencies..."
brew install automake libtool boost miniupnpc openssl@1.1 pkg-config protobuf qt libevent berkeley-db@5 librsvg

# Set OpenSSL and Berkeley DB flags
export LDFLAGS="-L$(brew --prefix openssl@1.1)/lib -L$(brew --prefix berkeley-db@5)/lib"
export CPPFLAGS="-I$(brew --prefix openssl@1.1)/include -I$(brew --prefix berkeley-db@5)/include"
export PKG_CONFIG_PATH="$(brew --prefix openssl@1.1)/lib/pkgconfig"

# Create install directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Clone Pepecoin source code
if [ -d "$INSTALL_DIR/pepecoin" ]; then
    echo "Pepecoin source code already exists at $INSTALL_DIR/pepecoin."
    read -p "Do you want to re-clone and replace it? (y/n): " RECLONE
    if [[ "$RECLONE" =~ ^[Yy]$ ]]; then
        echo "Removing existing source code..."
        rm -rf "$INSTALL_DIR/pepecoin"
        echo "Cloning Pepecoin source code..."
        git clone https://github.com/pepecoinppc/pepecoin.git
    else
        echo "Using existing Pepecoin source code."
    fi
else
    echo "Cloning Pepecoin source code..."
    git clone https://github.com/pepecoinppc/pepecoin.git
fi

cd pepecoin

# Build Pepecoin Core
echo "Building Pepecoin Core..."

./autogen.sh
./configure --with-gui=no --disable-tests
make

# Copy binaries to install directory
echo "Copying binaries to $INSTALL_DIR/bin..."
mkdir -p "$INSTALL_DIR/bin"
cp src/pepecoind "$INSTALL_DIR/bin/"
cp src/pepecoin-cli "$INSTALL_DIR/bin/"

# Ensure binaries have execute permissions
chmod +x "$INSTALL_DIR/bin/pepecoind"
chmod +x "$INSTALL_DIR/bin/pepecoin-cli"

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
if [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bash_profile"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
else
    SHELL_RC="$HOME/.profile"
fi
echo 'export PATH="'$INSTALL_DIR'/bin:$PATH"' >> "$SHELL_RC"
export PATH="$INSTALL_DIR/bin:$PATH"

echo "Please restart your terminal or run 'source $SHELL_RC' to update your PATH."

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
