#!/usr/bin/env python3
import os
import ssl
import http.server
import socketserver
import signal
import sys
import argparse
import shutil
import socket
import subprocess
import netifaces
from utility import Loader

# =========================
# Globals & ANSI
# =========================

should_cleanup = False

BOLD  = "\033[1m"
RESET = "\033[0m"
INFO  = "\033[1;34m"   # [i]
LINK  = "\033[1;90m"   # gray
CYAN  = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"

# =========================
# UI Helpers
# =========================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def get_terminal_height():
    try:
        return shutil.get_terminal_size().lines
    except Exception:
        return 24


def print_banner():
    banner = r"""
                _____      ______                                 
    ______ ____  ____(_)________  /_______________________   ______ 
    _  __ `/  / / /_  /_  ___/_  //_/_  ___/  _ \_  ___/_ | / /  _ \
    / /_/ // /_/ /_  / / /__ _  ,<  _(__  )/  __/  /   __ |/ //  __/
    \__, / \__,_/ /_/  \___/ /_/|_| /____/ \___//_/    _____/ \___/ 
     /_/                                                           
"""
    print(f"\033[1;96m{banner}{RESET}")


def print_line():
    print(f"{LINK}{'_' * 76}{RESET}")

# =========================
# Network Helpers
# =========================

def _local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_access_links(bind, secure=False):
    scheme = "https" if secure else "http"
    links = []

    if bind.startswith(("http://", "https://")):
        return [bind]

    if ":" in bind and bind.replace(".", "").replace(":", "").isdigit():
        ip, port = bind.split(":", 1)
        if ip == "0.0.0.0":
            links.extend([
                f"{scheme}://127.0.0.1:{port}",
                f"{scheme}://{_local_ip()}:{port}"
            ])
        else:
            links.append(f"{scheme}://{ip}:{port}")
        return links

    if bind.isdigit():
        links.extend([
            f"{scheme}://127.0.0.1:{bind}",
            f"{scheme}://{_local_ip()}:{bind}"
        ])

    return links


def print_access_links(bind, secure=False):
    links = get_access_links(bind, secure)

    if not links:
        print(f"\n{INFO}[i]{RESET} {BOLD}No valid access links found{RESET}")
        return

    print(f"\n{INFO}[i]{RESET} {BOLD}Web interface available at:{RESET}")
    for url in links:
        print(f"    {LINK}{url}{RESET}")
    print_line()


# =========================
# Server Info
# =========================

def print_server_info(directory, host, port, secure):
    abs_directory = os.path.abspath(directory)
    print_line()
    print(f"\n{INFO}[i]{RESET} {BOLD}Server Information:{RESET}")
    print(BOLD + f"  {'Root Dir':<10}:{GREEN}{abs_directory}{RESET}")
    print(BOLD + f"  {'Address':<10}: {YELLOW}{host}:{port}{RESET}")
    print(BOLD + f"  {'Secure':<10}: {'Yes' if secure else 'No'}{RESET}")
    print_line()

    return get_terminal_height() - 14

# =========================
# SSL
# =========================

def create_disposable_certificates():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cert_dir = os.path.join(script_dir, "certs")
    os.makedirs(cert_dir, exist_ok=True)

    key_path = os.path.join(cert_dir, "server.key")
    crt_path = os.path.join(cert_dir, "server.crt")

    loader = Loader(interval=0.2)
    loader.start("[i] Generating SSL certificate ")

    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:4096",
        "-keyout", key_path,
        "-out", crt_path,
        "-days", "365",
        "-nodes",
        "-subj", "/CN=localhost"
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    loader.stop()
    print(f"{INFO}[i]{RESET} Certificate created:")
    print(f"    {crt_path}")
    print(f"    {key_path}")

# =========================
# Server
# =========================

def run_http_server(directory, host, port, secure):
    print_server_info(directory, host, port, secure)

    handler = http.server.SimpleHTTPRequestHandler
    handler.directory = directory

    httpd = socketserver.TCPServer((host, port), handler)

    if secure:
        cert_dir = os.path.join(os.path.dirname(__file__), "certs")
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(
            os.path.join(cert_dir, "server.crt"),
            os.path.join(cert_dir, "server.key")
        )
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print_access_links(f"{host}:{port}", secure)
    print(f"{GREEN} [✓]{RESET} {BOLD}Server running — Ctrl+C to stop{RESET}")

    httpd.serve_forever()

# =========================
# Cleanup & Signals
# =========================

def handle_cleanup():
    cert_dir = os.path.join(os.path.dirname(__file__), "certs")
    if os.path.exists(cert_dir):
        shutil.rmtree(cert_dir)
        print(f"{INFO}[i]{RESET} Certificates cleaned up")
    sys.exit(0)


def signal_handler(sig, frame):
    print(f"\n{INFO}[i]{RESET} Shutting down…")
    handle_cleanup()

# =========================
# CLI
# =========================

def parse_arguments():
    p = argparse.ArgumentParser(description="QuickServe – Temporary HTTP/HTTPS server")
    p.add_argument("directory")
    p.add_argument("host")
    p.add_argument("port", type=int)
    p.add_argument("-s", "--secure", action="store_true")
    return p.parse_args()

# =========================
# Entry
# =========================

def main():
    args = parse_arguments()

    if args.secure:
        create_disposable_certificates()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    run_http_server(args.directory, args.host, args.port, args.secure)


if __name__ == "__main__":
    clear_screen()
    print_banner()
    main()
