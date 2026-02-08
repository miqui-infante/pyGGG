#!/bin/bash
# Uninstallation script for pyGGG

# List of candidate directories (same as install.sh)
CANDIDATES=(
    "$HOME/.local/bin"
    "$HOME/bin"
    "$HOME/opt/bin"
    "$HOME/.local/share/bin"
    "/usr/local/bin"
    "/usr/local/share/bin"
    "/opt/bin"
)

echo "pyGGG Uninstallation"
echo "===================="
echo

FOUND=false

# Search for installed commands in all candidate directories
for dir in "${CANDIDATES[@]}"; do
    if [ -f "$dir/ggg" ] || [ -f "$dir/gg" ]; then
        FOUND=true

        if [ -f "$dir/ggg" ]; then
            echo "Removing $dir/ggg..."
            rm "$dir/ggg"
            echo "✓ Removed ggg"
        fi

        if [ -f "$dir/gg" ]; then
            echo "Removing $dir/gg..."
            rm "$dir/gg"
            echo "✓ Removed gg"
        fi

        echo
    fi
done

if [ "$FOUND" = true ]; then
    echo "✓ Uninstallation complete!"
else
    echo "No pyGGG installation found."
    echo "Searched in:"
    for dir in "${CANDIDATES[@]}"; do
        echo "  - $dir"
    done
fi
