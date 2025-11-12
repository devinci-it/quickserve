# QuickServe

QuickServe is a simple HTTP/HTTPS server designed to quickly serve files from a specified directory. It supports both HTTP and HTTPS modes, with the ability to create temporary self-signed certificates for secure connections.

## Features

* Serve any directory on your local machine.
* Supports both HTTP and HTTPS (with self-signed certificates).
* Simple to install and use.

## Installation

### 1. Clone or download the repository

Clone the repository or download the files to your local machine.

```bash
git clone https://github.com/devici-it/quickserve.git
cd quickserve
```

### 2. Run the installation script

To install QuickServe, run the `install.sh` script. This will install the app and set up the required environment.

```bash
chmod +x install.sh
./install.sh
```

The script will:

* Install the app into `$HOME/.local/bin`.
* Create a Python virtual environment in `$HOME/.local/usr/lib/python3/quickserve/quickserve-venv`.
* Install any dependencies listed in `requirements.txt` (if available).

### 3. Add `$HOME/.local/bin` to your `PATH`

You can optionally add `$HOME/.local/bin` to your `PATH` so that the `quickserve` command can be run from anywhere.

The installation script will check your shell configuration file (`.bashrc` or `.zshrc`) and add the necessary line automatically.

```bash
# For bash:
echo "export PATH=\$PATH:$HOME/.local/bin" >> ~/.bashrc
source ~/.bashrc

# For zsh:
echo "export PATH=\$PATH:$HOME/.local/bin" >> ~/.zshrc
source ~/.zshrc
```

---

## Usage

### Run the Server

Once the installation is complete, you can start the QuickServe HTTP/HTTPS server using the following command:

```bash
quickserve <directory> <host> <port> [--secure]
```

* `<directory>`: The directory you want to serve. If not provided, it defaults to the current working directory.
* `<host>`: The host to bind to (e.g., `localhost`, `0.0.0.0`).
* `<port>`: The port to listen on (e.g., `8000`).
* `--secure`: Optional. If specified, the server will run with HTTPS using self-signed certificates.

#### Example

1. **Serve a directory over HTTP** (non-secure):

   ```bash
   quickserve /path/to/directory 0.0.0.0 8000
   ```

   This command will serve the files in `/path/to/directory` over HTTP on port 8000, and it will be accessible on all interfaces (`0.0.0.0`).

2. **Serve a directory over HTTPS** (secure):

   ```bash
   quickserve /path/to/directory 0.0.0.0 8000 --secure
   ```

   This command will serve the directory over HTTPS, using a self-signed certificate.

#### Notes on Directory Argument:

* If you do not specify a directory, it will default to the current working directory (`os.getcwd()`).
* Ensure the directory exists and contains the files you want to serve.

---

## Clean-Up

QuickServe generates self-signed SSL certificates when running in secure mode (`--secure`). If you wish to clean up these certificates, simply stop the server with `Ctrl+C` or `Esc`, and the app will prompt you to remove the generated files.

---

## Troubleshooting

### 1. **Directory Not Being Taken Correctly**

If the server fails to pick up the specified directory, ensure you're passing the full absolute path. If no directory is passed, the current working directory will be served by default.

**To fix this**:

* Ensure you run the command as shown in the examples above.
* If the bug persists, you can manually edit the command to specify the correct path to the directory.

### 2. **Missing Dependencies**

If the server fails due to missing dependencies, ensure that the `requirements.txt` file is present and that the installation was successful.

Run the following to install missing dependencies:

```bash
source ~/.local/usr/lib/python3/quickserve/quickserve-venv/bin/activate
pip install -r requirements.txt
```

### 3. **Server Not Running**

If the server does not start, ensure the port is open and not being used by another service. You can check this by running:

```bash
lsof -i :<port_number>
```

If the port is in use, either stop the conflicting service or choose another port.

---

## License

QuickServe is released under the MIT License.

---

## Contributions

Feel free to fork this repository, make improvements, and submit pull requests!



