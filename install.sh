#!/bin/bash
# Installation script for pyGGG

set -e

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

# List of candidate directories in priority order
CANDIDATES=(
    "$HOME/.local/bin"
    "$HOME/bin"
    "$HOME/opt/bin"
    "$HOME/.local/share/bin"
    "/usr/local/bin"
    "/usr/local/share/bin"
    "/opt/bin"
)

INSTALL_DIR=""
FALLBACK_DIR=""

# Find the best installation directory
for dir in "${CANDIDATES[@]}"; do
    # Check if directory exists and is writable
    if [ -d "$dir" ] && [ -w "$dir" ]; then
        # Check if it's in PATH (need to check both expanded and unexpanded paths)
        # Split PATH by : and check each entry
        IN_PATH=false
        IFS=':' read -ra PATH_ENTRIES <<< "$PATH"
        for path_entry in "${PATH_ENTRIES[@]}"; do
            # Expand ~ if present
            expanded_path="${path_entry/#\~/$HOME}"
            if [ "$expanded_path" = "$dir" ]; then
                IN_PATH=true
                break
            fi
        done

        if [ "$IN_PATH" = true ]; then
            # Perfect match: exists, writable, and in PATH
            INSTALL_DIR="$dir"
            echo "✓ Found installation directory: $INSTALL_DIR"
            break
        else
            # Good candidate but not in PATH - save as fallback
            if [ -z "$FALLBACK_DIR" ]; then
                FALLBACK_DIR="$dir"
            fi
        fi
    fi
done

# If no directory in PATH was found, use fallback or create ~/.local/bin
if [ -z "$INSTALL_DIR" ]; then
    if [ -n "$FALLBACK_DIR" ]; then
        # Use existing directory even if not in PATH
        INSTALL_DIR="$FALLBACK_DIR"
        echo "⚠ Using $INSTALL_DIR (not in PATH)"
    else
        # Create ~/.local/bin as default
        INSTALL_DIR="$HOME/.local/bin"
        echo "Creating $INSTALL_DIR..."
        mkdir -p "$INSTALL_DIR"
        echo "⚠ Created $INSTALL_DIR (not in PATH)"
    fi

    # Warn about PATH
    echo
    echo "Warning: $INSTALL_DIR is not in your PATH"
    echo "Add this line to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
    echo
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
    echo "✓ Commands are ready to use!"
else
    echo "Note: You may need to restart your shell or run:"
    echo "  source ~/.bashrc  (or ~/.zshrc if using zsh)"
fi
