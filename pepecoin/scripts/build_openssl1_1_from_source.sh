#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting build and installation of OpenSSL 1.1.1w from source on macOS..."

# Variables
OPENSSL_VERSION="1.1.1w"
OPENSSL_PREFIX="/usr/local/openssl-${OPENSSL_VERSION}"
OPENSSL_TARBALL="openssl-${OPENSSL_VERSION}.tar.gz"
OPENSSL_URL="https://www.openssl.org/source/old/1.1.1/${OPENSSL_TARBALL}"

# Check system architecture
arch=$(uname -m)
echo "Detected architecture: $arch"

# Check if the OpenSSL source tarball exists
if [[ -f "${OPENSSL_TARBALL}" ]]; then
    echo "OpenSSL source tarball ${OPENSSL_TARBALL} already exists."
    read -p "Do you want to re-download it? (y/n): " REDOWNLOAD
    if [[ "${REDOWNLOAD}" =~ ^[Yy]$ ]]; then
        echo "Re-downloading OpenSSL ${OPENSSL_VERSION} source code..."
        rm -f "${OPENSSL_TARBALL}"
        curl -O -L "${OPENSSL_URL}"
    else
        echo "Using existing OpenSSL source tarball."
    fi
else
    echo "Downloading OpenSSL ${OPENSSL_VERSION} source code..."
    curl -O -L "${OPENSSL_URL}"
fi

# Verify that the file was downloaded successfully
if [[ ! -f "${OPENSSL_TARBALL}" ]]; then
    echo "Error: Failed to download OpenSSL source code."
    exit 1
fi


# Extract the source code
echo "Extracting OpenSSL source code..."
tar -xzf "${OPENSSL_TARBALL}"

cd "openssl-${OPENSSL_VERSION}"

# Configure and build OpenSSL
echo "Configuring OpenSSL build..."

if [[ "$arch" == "arm64" ]]; then
    TARGET="darwin64-arm64-cc"
elif [[ "$arch" == "x86_64" ]]; then
    TARGET="darwin64-x86_64-cc"
else
    echo "Error: Unsupported architecture: $arch"
    exit 1
fi

./Configure "${TARGET}" --prefix="${OPENSSL_PREFIX}" no-shared no-async

echo "Building OpenSSL..."
make

echo "Installing OpenSSL..."
sudo make install

# Return to the original directory
cd ..

# Clean up
echo "Cleaning up..."
rm -rf "openssl-${OPENSSL_VERSION}"
rm -f "${OPENSSL_TARBALL}" "${OPENSSL_TARBALL}.sha256"

# Validate the installation
echo "Validating OpenSSL installation..."

if [ -f "${OPENSSL_PREFIX}/bin/openssl" ]; then
    echo "OpenSSL installed successfully at ${OPENSSL_PREFIX}."
else
    echo "Error: OpenSSL installation failed."
    exit 1
fi

# Display the installed version
installed_version=$("${OPENSSL_PREFIX}/bin/openssl" version)
echo "Installed OpenSSL version: $installed_version"

echo "Build and installation of OpenSSL ${OPENSSL_VERSION} completed successfully."
