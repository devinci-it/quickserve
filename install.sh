#!/bin/bash

# Define variables
INSTALL_DIR="$HOME/.local/bin"                               # Installation directory for the app
APP_DIR="$HOME/.local/usr/lib/python3/quickserve"            # New directory for the app's files
VENV_DIR="$APP_DIR/quickserve-venv"                           # Directory for the virtual environment
APP_NAME="quickserve"                                         # Name of the app (can be adjusted)
APP_SOURCE_DIR=$(pwd)                                         # Current directory of the script (app source directory)
APP_SCRIPT="quickserve.py"                                    # Python script to install
REQUIREMENTS_FILE="requirements.txt"                          # Dependencies file (if available)

# Ensure the installation directory exists
echo "Ensuring installation directory exists at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

# Ensure the application directory exists
echo "Ensuring application directory exists at $APP_DIR..."
mkdir -p "$APP_DIR"

# Move the contents of the current directory to $APP_DIR
echo "Moving application files from $APP_SOURCE_DIR to $APP_DIR..."
cp -r "$APP_SOURCE_DIR/"* "$APP_DIR"  # Copy files from current directory to the app directory

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating a virtual environment at $VENV_DIR..."
  python3 -m venv "$VENV_DIR"
else
  echo "Virtual environment already exists at $VENV_DIR."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies if requirements.txt is available
if [ -f "$APP_DIR/$REQUIREMENTS_FILE" ]; then
  echo "Installing dependencies from $REQUIREMENTS_FILE..."
  pip install --upgrade pip  # Upgrade pip to the latest version
  pip install -r "$APP_DIR/$REQUIREMENTS_FILE"  # Install from requirements.txt
else
  echo "No $REQUIREMENTS_FILE found. Skipping dependency installation."
fi

# Create a wrapper script to run the Python application within the virtual environment
echo "Creating a wrapper script for $APP_NAME..."
cat > "$INSTALL_DIR/$APP_NAME" <<EOL
#!/bin/bash
# Activate the virtual environment and run the Python app using the virtualenv's Python
source "$VENV_DIR/bin/activate"
"$VENV_DIR/bin/python" "$APP_DIR/$APP_SCRIPT" "\$@"
EOL

# Make the wrapper script executable
chmod +x "$INSTALL_DIR/$APP_NAME"

# Output instructions for the user
echo "Installation complete!"
echo "To run the app, use: $INSTALL_DIR/$APP_NAME <directory> <host> <port> [--secure]"
echo "You can add $INSTALL_DIR to your PATH to use it from anywhere."

# Optionally, add $INSTALL_DIR to the user's PATH if not already added
if ! grep -q "$INSTALL_DIR" "$HOME/.bashrc" && ! grep -q "$INSTALL_DIR" "$HOME/.zshrc"; then
  echo "Adding $INSTALL_DIR to your PATH..."
  # Check if user uses bash or zsh and add the path accordingly
  if [ -f "$HOME/.bashrc" ]; then
    echo "export PATH=\$PATH:$INSTALL_DIR" >> "$HOME/.bashrc"
    echo "Added to $HOME/.bashrc. Please run 'source ~/.bashrc' to update your PATH."
  elif [ -f "$HOME/.zshrc" ]; then
    echo "export PATH=\$PATH:$INSTALL_DIR" >> "$HOME/.zshrc"
    echo "Added to $HOME/.zshrc. Please run 'source ~/.zshrc' to update your PATH."
  else
    echo "Neither .bashrc nor .zshrc found. Please manually add $INSTALL_DIR to your PATH."
  fi
else
  echo "$INSTALL_DIR is already in your PATH."
fi

# Final message
echo "Installation completed successfully."
