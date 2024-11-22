from setuptools import setup, find_packages
import setuptools
import subprocess
import os

setup(
    name='pepecoin',  # Package name
    version='0.0.1',  # Version of your package
    author='PEPE',  # Your name

    scripts=[
            'scripts/setup_pepecoin_node.sh',
            'scripts/setup_pepecoin_node_macos.sh',
            'scripts/virgin_vm.sh',
        ],
    data_files=[
            # You can specify where to install the service file
            # For example, installing it to /etc/systemd/system (requires sudo)
            # Commented out because it may not be appropriate for all users
            # ('/etc/systemd/system', ['scripts/pepecoind.service']),
        ],
    description='PEPECOIN class to interact with pepecoin blockchain in a easy way',  # Short description
    long_description=open('README.md').read(),  # Long description from a README file
    long_description_content_type='text/markdown',  # Type of the long description
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pepecoin-monitor=pepecoin.cli:monitor_node',
            'pepecoin-setup=pepecoin.cli:setup_node',
            'pepecoin-setup-macos=pepecoin.cli:setup_node_macos',  # Ensure this function exists
            'pepecoin-setup-vm=pepecoin.cli:setup_vm',  # Ensure this function exists
            'pepecoin-install-service=pepecoin.cli:install_service',  # Ensure this function exists
        ],
    },
    packages=find_packages(),  # Automatically find packages in the directory
    install_requires=['pydantic',
                        'requests',
                        'indented_logger',
                        'pyyaml',
                        'python-bitcoinrpc',
                        'python-dotenv',
                        'python-bitcoinrpc' ],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Development status
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',  # License as you choose
        'Programming Language :: Python :: 3',  # Supported Python versions
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',  # Minimum version requirement of Python
)