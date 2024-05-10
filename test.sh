PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

source "$PROJECT_DIR/.venv/bin/activate"

python3 "$PROJECT_DIR/src/test.py"

deactivate