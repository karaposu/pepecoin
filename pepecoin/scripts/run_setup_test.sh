#!/usr/bin/env bash

# Exit on errors
set -e

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
echo "Running pepecoin.test_pepecoin..."
python -m pepecoin.test_pepecoin
