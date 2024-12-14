# pepecoin/cli.py

import click
import subprocess
import os

@click.group()
def cli():
    """Pepecoin CLI utility."""
    pass

@cli.command()
def setup_node():
    """
    Run the Pepecoin node setup script for Linux.
    """
    # Determine the path to the Linux setup script
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setup_pepecoin_node.sh')
    script_path = os.path.abspath(script_path)

    # Check if the script exists
    if not os.path.isfile(script_path):
        click.echo(f"Setup script not found at {script_path}")
        return

    # Make the script executable
    os.chmod(script_path, 0o755)

    # Execute the setup script
    try:
        subprocess.run(['bash', script_path], check=True)
        click.echo("Pepecoin node setup completed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred during setup: {e}")




@cli.command()
def run_transfer_test():
    """
    Run the Pepecoin node setup script for Linux.
    """
    # Determine the path to the Linux setup script
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'run_transfer_test.sh')
    script_path = os.path.abspath(script_path)

    # Check if the script exists
    if not os.path.isfile(script_path):
        click.echo(f"script not found at {script_path}")
        return

    # Make the script executable
    os.chmod(script_path, 0o755)

    # Execute the setup script
    try:
        subprocess.run(['bash', script_path], check=True)
        click.echo("Transfer Test executed. Please inspect output for validation.")
    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred during test: {e}")


@cli.command()
def run_setup_test():
    """
    Run the Pepecoin node setup script for Linux.
    """
    # Determine the path to the Linux setup script
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'run_setup_test.sh')
    script_path = os.path.abspath(script_path)

    # Check if the script exists
    if not os.path.isfile(script_path):
        click.echo(f"script not found at {script_path}")
        return

    # Make the script executable
    os.chmod(script_path, 0o755)

    # Execute the setup script
    try:
        subprocess.run(['bash', script_path], check=True)
        click.echo("Test executed. Please inspect output for validation.")
    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred during test: {e}")

@cli.command()
def setup_node_macos():
    """
    Run the Pepecoin node setup script for macOS.
    """
    # Determine the path to the macOS setup script
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'setup_pepecoin_node_macos.sh')
    script_path = os.path.abspath(script_path)

    # Check if the script exists
    if not os.path.isfile(script_path):
        click.echo(f"macOS setup script not found at {script_path}")
        return

    # Make the script executable
    os.chmod(script_path, 0o755)

    # Execute the setup script
    try:
        subprocess.run(['bash', script_path], check=True)
        click.echo("Pepecoin node setup for macOS completed successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"An error occurred during macOS setup: {e}")

if __name__ == '__main__':
    cli()
