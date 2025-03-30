#!/bin/bash

set -e

echo "Installing command: kluster"


if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip3 install -e .

chmod +x kluster.py

echo "Creating symbolic link: /usr/local/bin..."
sudo ln -sf "$(pwd)/kluster.py" /usr/local/bin/kluster

echo "Installation complete"
