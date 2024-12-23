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
brew install automake libtool boost miniupnpc pkg-config protobuf qt libevent berkeley-db@5 librsvg

# Set OpenSSL, Berkeley DB, and Boost prefixes
export OPENSSL_PREFIX="/usr/local/openssl-1.1.1w"
export BERKELEY_DB_PREFIX="$(brew --prefix berkeley-db@5)"
export BOOST_PREFIX="$(brew --prefix boost)"

# Validate OpenSSL installation
if [ ! -f "${OPENSSL_PREFIX}/bin/openssl" ]; then
    echo "Error: OpenSSL not found at ${OPENSSL_PREFIX}. Please ensure OpenSSL is installed correctly."
    exit 1
fi

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

# Apply patches to replace deprecated Boost filesystem functions
echo "Applying Boost filesystem patches..."

# Correct the handling of walletFile in wallet.cpp
sed -i '' 's/boost::filesystem::basename(\([^)]*\))/boost::filesystem::path(\1).stem().string()/g' src/wallet/wallet.cpp
sed -i '' 's/boost::filesystem::extension(\([^)]*\))/boost::filesystem::path(\1).extension().string()/g' src/wallet/wallet.cpp



## Replace 'copy_option::overwrite_if_exists' with 'copy_options::overwrite_existing'
sed -i '' 's/boost::filesystem::copy_option::overwrite_if_exists/boost::filesystem::copy_options::overwrite_existing/g' src/wallet/wallet.cpp
sed -i '' 's/\bboost::filesystem::copy_option::overwrite_if_exists\b/boost::filesystem::copy_options::overwrite_existing/g' src/wallet/wallet.cpp
#

## Replace any remaining 'boost::filesystem::copy_option' with 'boost::filesystem::copy_options'
#sed -i '' 's/\bboost::filesystem::copy_option\b/boost::filesystem::copy_options/g' src/wallet/wallet.cpp
#
#
#
## Replace 'copy_option::overwrite_if_exists' with 'copy_options::overwrite_existing'
#
#
## Replace 'copy_option' with 'copy_options' only if not already modified
#sed -i '' '/copy_options::overwrite_existing/!s/\bboost::filesystem::copy_option\b/boost::filesystem::copy_options/g' src/wallet/wallet.cpp
## Remove previous attempt to replace random_shuffle
## No need to replace random_shuffle if we suppress the deprecation warning

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

# Clean previous builds if Makefile exists
if [ -f Makefile ]; then
    make clean
fi

# Build Pepecoin Core
echo "Building Pepecoin Core..."

# Use Clang as the compiler
export CC=clang
export CXX=clang++

# Validation 2: Test compiler's ability to include C++ Standard Library headers
echo "Checking compiler's ability to include C++ Standard Library headers..."
echo '#include <list>
int main() {
    std::list<int> myList;
    return 0;
}' > test_std_list.cpp

if ! $CXX $CXXFLAGS test_std_list.cpp -o test_std_list >/dev/null 2>&1; then
    echo "Error: Compiler cannot compile a simple program using std::list."
    rm -f test_std_list.cpp
    exit 1
fi
rm -f test_std_list.cpp test_std_list
echo "Compiler can include C++ Standard Library headers."

./autogen.sh
./configure --with-gui=no --disable-tests --with-boost="${BOOST_PREFIX}"
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
if ! grep -q 'export PATH="'$INSTALL_DIR'/bin:$PATH"' "$SHELL_RC"; then
    echo 'export PATH="'$INSTALL_DIR'/bin:$PATH"' >> "$SHELL_RC"
    echo "Please restart your terminal or run 'source $SHELL_RC' to update your PATH."
fi
export PATH="$INSTALL_DIR/bin:$PATH"

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





