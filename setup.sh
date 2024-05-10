#!/bin/bash

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

python3 -m venv "$PROJECT_DIR/.venv"

source "$PROJECT_DIR/.venv/bin/activate"

pip install -r "$PROJECT_DIR/requirements.txt"

deactivate

chmod +x "$PROJECT_DIR/rd-gen"

if [[ ":$PATH:" != *":$PROJECT_DIR:"* ]]; then
    echo "export PATH=\"\$PATH:$PROJECT_DIR\"" >> ~/.bashrc
fi

echo "Road Network Generator was installed successfully."
