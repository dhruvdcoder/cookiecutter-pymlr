#!/bin/bash 
set -x
conda create -p ./.venv_cookiecutter-pymlr python=3.9 pip
conda activate ./.venv_cookiecutter-pymlr
pip install -r requirements.txt

set +x
