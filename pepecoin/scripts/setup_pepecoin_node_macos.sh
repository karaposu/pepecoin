#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

###############################################################################
# Preliminary Information
###############################################################################

# Okay, This script works for macOS 15.1.1. But there are some duct tape requirements.
# 1. With macOS 14 it does not work.
# 2. Xcode should be installed via the App Store and also the command line tools.
# 3. OpenSSL 1.1 is disabled in Homebrew, so we are getting it from somewhere else and building it from scratch.
# 4. The world is a messy place, yet there are meaningful events. And there is a possibility that they might be worth the pain, or not.
# 5. In this code, there are some patches for Boost 1.86. I am not entirely sure how much they affect the end application.
# 6. Use this for local Pepecoin development and do not use it in production.

###############################################################################
# Variables
###############################################################################

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

###############################################################################
# Dependency Installation
###############################################################################

# Install Xcode command line tools if not installed
if ! xcode-select -p &>/dev/null; then
    echo "Installing Xcode command line tools..."
    xcode-select --install
    echo "Please complete the installation of Xcode command line tools and rerun this script."
    exit 1
fi

# Install Xcode from App Store (Assuming user has installed it manually as per the preliminary note)

# Install Homebrew if not installed
if ! command -v brew &>/dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Update Homebrew
echo "Updating Homebrew..."
brew update

# Reinstall dependencies from source
echo "Reinstalling dependencies from source..."
brew reinstall --build-from-source berkeley-db@5 libevent
brew reinstall --build-from-source boost

# Install other dependencies
echo "Installing other dependencies..."
brew install automake libtool miniupnpc pkg-config protobuf qt librsvg

###############################################################################
# OpenSSL 1.1 Installation
###############################################################################

# Note: OpenSSL 1.1 is disabled in Homebrew. We'll build it from source using the provided script.

# Set OpenSSL prefix
OPENSSL_PREFIX="/usr/local/openssl-1.1.1w"

# Check if OpenSSL 1.1 is installed
if [ ! -f "${OPENSSL_PREFIX}/bin/openssl" ]; then
    echo "OpenSSL 1.1 not found at ${OPENSSL_PREFIX}. Building OpenSSL 1.1 from source..."
    # Ensure the build script is executable
    if [ ! -x "./build_openssl1_1_from_source.sh" ]; then
        echo "Making build_openssl1_1_from_source.sh executable..."
        chmod +x ./build_openssl1_1_from_source.sh
    fi
    # Run the build script
    ./build_openssl1_1_from_source.sh
else
    echo "OpenSSL 1.1 is already installed at ${OPENSSL_PREFIX}."
fi

# Validate OpenSSL installation
if [ ! -f "${OPENSSL_PREFIX}/bin/openssl" ]; then
    echo "Error: OpenSSL 1.1 installation failed."
    exit 1
fi

###############################################################################
# Environment Variable Setup
###############################################################################

# Set Berkeley DB and Boost prefixes
export BERKELEY_DB_PREFIX="$(brew --prefix berkeley-db@5)"
export BOOST_PREFIX="$(brew --prefix boost)"

# Display OpenSSL version
echo "Using OpenSSL version:"
"${OPENSSL_PREFIX}/bin/openssl" version

# Validate Boost installation
if [ ! -d "${BOOST_PREFIX}/include/boost" ]; then
    echo "Error: Boost not found at ${BOOST_PREFIX}. Please ensure Boost is installed correctly."
    exit 1
fi

# Display Boost version
BOOST_VERSION_HEADER="${BOOST_PREFIX}/include/boost/version.hpp"
if [ -f "${BOOST_VERSION_HEADER}" ]; then
    BOOST_VERSION=$(grep "#define BOOST_LIB_VERSION" "${BOOST_VERSION_HEADER}" | awk '{print $3}' | tr -d '"')
    echo "Using Boost version: ${BOOST_VERSION}"
else
    echo "Could not determine Boost version."
fi

# Set environment variables
export LDFLAGS="-L${OPENSSL_PREFIX}/lib -L${BERKELEY_DB_PREFIX}/lib -L${BOOST_PREFIX}/lib"
export CPPFLAGS="-I${OPENSSL_PREFIX}/include -I${BERKELEY_DB_PREFIX}/include -I${BOOST_PREFIX}/include -DHAVE_BUILD_INFO -D__STDC_FORMAT_MACROS -DMAC_OSX -DOBJC_OLD_DISPATCH_PROTOTYPES=0"
export PKG_CONFIG_PATH="${OPENSSL_PREFIX}/lib/pkgconfig"
export BOOST_ROOT="${BOOST_PREFIX}"
export CXXFLAGS="-std=c++14 -Wno-deprecated-declarations"

# Remove conflicting include paths
if [[ "$CPPFLAGS" == *"/opt/local/include"* ]]; then
    echo "Removing conflicting include path /opt/local/include from CPPFLAGS."
    export CPPFLAGS="${CPPFLAGS//-I\/opt\/local\/include/}"
fi

# Verify that /opt/local/include is not in CPPFLAGS
if [[ "$CPPFLAGS" == *"/opt/local/include"* ]]; then
    echo "Error: Conflicting include path /opt/local/include still present in CPPFLAGS."
    exit 1
fi

# Validate LDFLAGS and CPPFLAGS for Berkeley DB paths
if [[ "$LDFLAGS" != *"${BERKELEY_DB_PREFIX}/lib"* ]]; then
    echo "Error: LDFLAGS does not contain Berkeley DB lib path."
    exit 1
fi

if [[ "$CPPFLAGS" != *"${BERKELEY_DB_PREFIX}/include"* ]]; then
    echo "Error: CPPFLAGS does not contain Berkeley DB include path."
    exit 1
fi

###############################################################################
# Source Code Setup
###############################################################################

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

###############################################################################
# Patching Source Code
###############################################################################

# Apply patches to replace deprecated Boost filesystem functions
echo "Applying Boost filesystem patches..."

# Correct the handling of walletFile in wallet.cpp
sed -i '' 's/boost::filesystem::basename(\([^)]*\))/boost::filesystem::path(\1).stem().string()/g' src/wallet/wallet.cpp
sed -i '' 's/boost::filesystem::extension(\([^)]*\))/boost::filesystem::path(\1).extension().string()/g' src/wallet/wallet.cpp

# Replace 'copy_option::overwrite_if_exists' with 'copy_options::overwrite_existing'
sed -i '' 's/\bboost::filesystem::copy_option::overwrite_if_exists\b/boost::filesystem::copy_options::overwrite_existing/g' src/wallet/wallet.cpp

# Replace any remaining 'boost::filesystem::copy_option' with 'boost::filesystem::copy_options'
sed -i '' 's/\bboost::filesystem::copy_option\b/boost::filesystem::copy_options/g' src/wallet/wallet.cpp

# Apply patches to replace is_complete() with is_absolute()
echo "Applying patches to replace is_complete() with is_absolute()..."
FILES_WITH_IS_COMPLETE=$(grep -rl "is_complete()" src/ || true)
if [ -n "$FILES_WITH_IS_COMPLETE" ]; then
    for FILE in $FILES_WITH_IS_COMPLETE; do
        sed -i '' 's/\.is_complete()/\.is_absolute()/g' "$FILE"
        echo "Patched $FILE"
    done
    echo "All patches applied successfully."
else
    echo "No patches needed. Code already uses is_absolute()."
    fi

###############################################################################
# Validation
###############################################################################

# Validation 1: Check if <list> header is included
VALIDATION_H="src/validation.h"
if ! grep -q "#include <list>" "$VALIDATION_H"; then
    echo "Adding #include <list> to $VALIDATION_H"
    sed -i '' '/#include <vector>/a\
#include <list>
' "$VALIDATION_H"
fi

# Validate that <list> is now included
if ! grep -q "#include <list>" "$VALIDATION_H"; then
    echo "Error: Failed to include <list> in $VALIDATION_H"
    exit 1
fi

# Validation 2: Test compiler's ability to include C++ Standard Library headers
echo "Checking compiler's ability to include C++ Standard Library headers..."
echo '#include <list>
int main() {
    std::list<int> myList;
    return 0;
}' > test_std_list.cpp

if ! clang++ $CXXFLAGS test_std_list.cpp -o test_std_list >/dev/null 2>&1; then
    echo "Error: Compiler cannot compile a simple program using std::list."
    rm -f test_std_list.cpp
    exit 1
fi
rm -f test_std_list.cpp test_std_list
echo "Compiler can include C++ Standard Library headers."

###############################################################################
# Compilation
###############################################################################

# Clean previous builds if Makefile exists
if [ -f Makefile ]; then
    make clean
fi

# Build Pepecoin Core
echo "Building Pepecoin Core..."

# Use Clang as the compiler
export CC=clang
export CXX=clang++

./autogen.sh
./configure --with-gui=no --disable-tests --with-boost="${BOOST_PREFIX}"
make

###############################################################################
# Installation
###############################################################################

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
if ! grep -q 'export PATH="'$INSTALL_DIR'/bin:$PATH"' "$SHELL_RC"; then
    echo 'export PATH="'$INSTALL_DIR'/bin:$PATH"' >> "$SHELL_RC"
    echo "Please restart your terminal or run 'source $SHELL_RC' to update your PATH."
fi
export PATH="$INSTALL_DIR/bin:$PATH"

###############################################################################
# Running the Daemon
###############################################################################

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
    # Check logs for more information
    tail -n 50 "$DATA_DIR/debug.log"
    exit 1
fi

echo "Pepecoin node setup completed successfully."
