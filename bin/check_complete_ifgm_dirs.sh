#!/bin/bash
set -e

# Directory containing interferograms
IFG_DIR="ifgms"

# Define key patterns that must exist in a complete directory
REQUIRED_PATTERNS=("*.unw")

for d in "$IFG_DIR"/*-*/; do
    missing=0
    echo "Checking $d ..."
    for pattern in "${REQUIRED_PATTERNS[@]}"; do
        shopt -s nullglob
        files=("$d"/$pattern)
        shopt -u nullglob
        if [ ${#files[@]} -eq 0 ]; then
            echo "   ❌ Missing $pattern"
            missing=1
        fi
    done

    if [ $missing -eq 0 ]; then
        echo "   ✅ Complete"
    else
        echo "   ⚠ Incomplete"
        read -p "   👉 Delete $d ? [y/N]: " confirm
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            rm -rf "$d"
            echo "   🗑 Deleted $d"
        else
            echo "   ⏩ Kept $d"
        fi
    fi
done

