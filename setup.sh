#!/bin/bash
set -e

if [ -d "./.venv/" ]; then
    echo "Removing existing .venv/ folder to replace it with a new installation."
    rm -Rf ./.venv/
fi

echo "Creating new .venv/ environment."
python3 -m venv ./.venv/
. ./.venv/bin/activate
echo "Installating Python dependencies."
pip install -r requirements.txt

echo ""
echo "Installation is done!"
