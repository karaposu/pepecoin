# pepecoin/cli.py

import click
import subprocess
import os

@click.command()
def setup_node():
    """
    Run the Pepecoin node setup script.
    """
    # Determine the path to the setup script
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'setup_pepecoin_node.sh')
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

if __name__ == '__main__':
    setup_node()
