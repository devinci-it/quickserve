import os
import ssl
import http.server
import socketserver
import signal
import sys
import argparse
import shutil
import time
import socket
import netifaces  # To fetch IP addresses for all network interfaces

# Global flag to handle clean-up confirmation
should_cleanup = False

# Function to clear the terminal screen (used only at the start)
def clear_screen():
    """Clear the terminal screen based on the OS (Windows or UNIX-based)."""
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to get the terminal height
def get_terminal_height():
    """Get the height of the terminal screen."""
    try:
        return shutil.get_terminal_size().lines
    except AttributeError:
        # If the terminal doesn't support this method, default to 24 lines
        return 24

# Function to print the server information
def print_server_info(directory, host, port, secure):
    """Print information about the server being started."""
    terminal_height = get_terminal_height()  # Get the terminal height
    banner_height = 6  # Set a height for the banner (adjustable)

    # Print the sticky banner (will be at the bottom of the terminal)
    print("=" * 40)
    print(f" QuickServe - Serving directory: {directory}")
    print(f" Address: {host}:{port}")
    print(f" Secure: {'Yes' if secure else 'No'}")
    print("=" * 40)
    print(" URI Endpoints:")
    print(f" - / (root directory: {directory})")
    print("=" * 40)

    # Return remaining space for log content
    return terminal_height - banner_height

# Function to create disposable certificates if required for SSL
def create_disposable_certificates():
    """Create temporary self-signed certificates for HTTPS."""
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cert_dir = os.path.join(script_dir, "certs")

    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    # Create a temporary self-signed certificate and key in the script's directory
    os.system(f"openssl req -x509 -newkey rsa:4096 -keyout {cert_dir}/server.key -out {cert_dir}/server.crt -days 365 -nodes -subj '/CN=localhost'")

# Function to get the local IP addresses of the system
def get_local_ip_addresses():
    """Get a list of local IP addresses from network interfaces."""
    ip_addresses = []
    for interface in netifaces.interfaces():
        try:
            # Get the interface's addresses
            addrs = netifaces.ifaddresses(interface)
            # Look for IPv4 addresses
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    ip_addresses.append(addr['addr'])
        except ValueError:
            continue
    return ip_addresses

# Function to handle starting the HTTP/HTTPS server
def run_http_server(directory, host, port, secure):
    """Start the HTTP/HTTPS server with the given parameters."""
    # Print server info (clear screen and display settings)
    log_height = print_server_info(directory, host, port, secure)

    # Create a simple HTTP request handler
    handler = http.server.SimpleHTTPRequestHandler
    handler.directory = directory  # Set the directory to be served

    if host == "0.0.0.0":
        # If the host is 0.0.0.0, print the local IP addresses
        print("\nAvailable IP addresses:")
        ip_addresses = get_local_ip_addresses()
        for ip in ip_addresses:
            print(f" - {ip}")
        print("=" * 40)

    try:
        if secure:
            # Setup SSL for HTTPS if secure flag is true
            print("Setting up HTTPS...")
            httpd = socketserver.TCPServer((host, port), handler)

            # Set up SSL context and load the certificate and key
            cert_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs")
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile=os.path.join(cert_dir, "server.crt"), keyfile=os.path.join(cert_dir, "server.key"))

            # Wrap the server socket with SSL (secure connection)
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

            print("Server running with SSL (HTTPS)...")
        else:
            # Non-SSL version (HTTP)
            print("Setting up HTTP...")
            httpd = socketserver.TCPServer((host, port), handler)
            print("Server running without SSL (HTTP)...")

        # Starting the server
        print(f"Starting server on {host}:{port}...")
        httpd.serve_forever()  # Use serve_forever to keep the server running

    except Exception as e:
        print(f"Error starting the server: {e}")

# Handle cleanup on exit (whether Ctrl+C, Esc, or other signals)
def handle_cleanup():
    """Perform clean-up tasks like removing disposable certificates."""
    global should_cleanup

    # If flagged for clean-up, proceed to delete the certs
    if should_cleanup:
        print("\nCleaning up generated certificates...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        cert_dir = os.path.join(script_dir, "certs")

        if os.path.exists(os.path.join(cert_dir, "server.crt")):
            os.remove(os.path.join(cert_dir, "server.crt"))
        if os.path.exists(os.path.join(cert_dir, "server.key")):
            os.remove(os.path.join(cert_dir, "server.key"))
        print("Clean-up complete!")
    else:
        # Prompt user to confirm clean-up
        confirm = input("Do you want to clean up generated files (certs)? [y/N]: ")
        if confirm.lower() == 'y':
            print("\nCleaning up generated certificates...")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            cert_dir = os.path.join(script_dir, "certs")

            if os.path.exists(os.path.join(cert_dir, "server.crt")):
                os.remove(os.path.join(cert_dir, "server.crt"))
            if os.path.exists(os.path.join(cert_dir, "server.key")):
                os.remove(os.path.join(cert_dir, "server.key"))
            print("Clean-up complete!")
        else:
            print("No clean-up performed.")

    sys.exit(0)  # Exit the program after cleanup

# Function to handle signal interruptions (Ctrl+C, Esc, etc.)
def signal_handler(sig, frame):
    """Handle interruption signals (e.g., Ctrl+C or Esc)."""
    global should_cleanup
    print("\nCaught Ctrl+C or Esc - Preparing for cleanup.")
    should_cleanup = True
    handle_cleanup()

# Function to handle user suspending the process (Ctrl+Z)
def suspend_handler(sig, frame):
    """Handle suspend signal (Ctrl+Z) to inform the user."""
    print("\nProcess suspended (Ctrl+Z). Press 'fg' to resume.")
    print("You can exit the program and clean up after resuming.")
    signal.signal(signal.SIGTSTP, signal.SIG_IGN)  # Ignore further suspend signals

# Setup command-line argument parsing
def parse_arguments():
    """Parse and return command-line arguments."""
    parser = argparse.ArgumentParser(description="QuickServe: Temporary HTTPS server")
    parser.add_argument("directory", help="Path to the directory to serve")
    parser.add_argument("host", help="Host address (e.g., 'localhost')")
    parser.add_argument("port", type=int, help="Port number (e.g., 8000)")
    parser.add_argument("--secure", "-s", action="store_true", help="Enable HTTPS (SSL)")
    return parser.parse_args()

# Main function to run the app
def main():
    """Main entry point for the script to start the server."""
    # Parse command-line arguments
    args = parse_arguments()

    # Create certificates if SSL is enabled
    if args.secure:
        create_disposable_certificates()

    # Set up signal handlers for clean exits (Ctrl+C, Esc, Ctrl+Z)
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Exit signal
    signal.signal(signal.SIGTSTP, suspend_handler)  # Ctrl+Z (suspend)

    # Run the server with the provided arguments
    run_http_server(args.directory, args.host, args.port, args.secure)

# Entry point
if __name__ == "__main__":
    main()

