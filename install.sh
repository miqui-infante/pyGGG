#!/bin/bash
# Installation script for pyGGG

set -e

INSTALL_DIR="$HOME/.local/bin"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="$SCRIPT_DIR/pyggg.py"

echo "pyGGG Installation"
echo "=================="
echo

# Check if source script exists
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "Error: pyggg.py not found in $SCRIPT_DIR"
    exit 1
fi

# Create ~/.local/bin if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
fi

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "Warning: $INSTALL_DIR is not in your PATH"
    echo
    echo "Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install ggg (copy)
echo "Installing ggg to $INSTALL_DIR/ggg..."
cp "$SOURCE_SCRIPT" "$INSTALL_DIR/ggg"
chmod +x "$INSTALL_DIR/ggg"

# Install gg (wrapper script)
echo "Installing gg to $INSTALL_DIR/gg..."
cat > "$INSTALL_DIR/gg" << 'EOF'
#!/bin/bash
exec ggg "$@" | less -S
EOF
chmod +x "$INSTALL_DIR/gg"

echo
echo "✓ Installation complete!"
echo
echo "Available commands:"
echo "  ggg    - Generate git graph (stdout)"
echo "  gg     - Generate git graph (interactive with less)"
echo
echo "Usage examples:"
echo "  ggg                    # Current repo to stdout"
echo "  ggg > output.txt       # Save to file"
echo "  ggg | head -20         # First 20 lines"
echo "  gg                     # Interactive view with less"
echo

# Test if commands are available
if command -v ggg &> /dev/null && command -v gg &> /dev/null; then
    echo "Commands are ready to use!"
else
    echo "Note: You may need to restart your shell or run:"
    echo "  source ~/.bashrc  (or ~/.zshrc if using zsh)"
fi
