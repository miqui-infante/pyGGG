#!/bin/bash
# Uninstallation script for pyGGG

INSTALL_DIR="$HOME/.local/bin"

echo "pyGGG Uninstallation"
echo "===================="
echo

if [ -f "$INSTALL_DIR/ggg" ]; then
    echo "Removing $INSTALL_DIR/ggg..."
    rm "$INSTALL_DIR/ggg"
    echo "✓ Removed ggg"
fi

if [ -f "$INSTALL_DIR/gg" ]; then
    echo "Removing $INSTALL_DIR/gg..."
    rm "$INSTALL_DIR/gg"
    echo "✓ Removed gg"
fi

echo
echo "✓ Uninstallation complete!"
