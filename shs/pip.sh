#!/bin/bash

# use bash strict mode
set -euo pipefail

# Activate the virtual environment and install dependencies
source $HOME/www/python/venv/bin/activate

pip install pip -U
pip install -r $HOME/www/python/src/requirements.txt -U
pip uninstall fix_refs -y
pip install git+https://github.com/MrIbrahem/fix_refs_new_py.git -U
# toolforge-jobs run update --image python3.13 --command "~/shs/update.sh && ~/shs/pip.sh" --wait
