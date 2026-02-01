#!/bin/bash
# toolforge-jobs run update --image python3.11 --command "~/shs/update.sh" --wait

set -euo pipefail

export SUB_DIR_COPY="src"
export COPY_TO_TARGET="requirements.txt"
export CLEAN_INSTALL=1
export USER_NAME="MrIbrahem"
export PYTHON_BIN="python3"
BRANCH="${1:-main}"
REPO=publish_py
TARGET_PATH=~/www/python/src
$HOME/shs/deploy_repo.sh "$REPO" "$TARGET_PATH" "$BRANCH"

if source "$HOME/www/python/venv/bin/activate"; then
    pip install -r $HOME/www/python/src/requirements.txt
    # exit 1
else
    echo "Failed to activate virtual environment" >&2
fi
