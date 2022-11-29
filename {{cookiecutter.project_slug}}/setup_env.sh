#!/bin/bash
set -xeuo pipefail
export CONDA_ALWAYS_YES="true"
conda init --all
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
else
    source ~/.bash_profile
fi
echo "=======Creating virtual env========="
{% if cookiecutter.venv_tool == "conda" %}
conda create -p ./.venv_{{cookiecutter.project_slug}} python={{cookiecutter.python_version}} pip
conda activate ./.venv_{{cookiecutter.project_slug}}
{% elif cookiecutter.venv_tool == "virtualenv" %}
python3 -m virtualenv  .venv_{{cookiecutter.project_slug}}
source .venv_{{cookiecutter.project_slug}}/bin/activate
{% endif %}

echo "=======Install test requirements======="
pip install -r test_requirements.txt

echo "=======Install doc requirements======="
pip install -r doc_requirements.txt

echo "========Create log dir for single runs========="
mkdir -p logs
{% if cookiecutter.use_wandb =="y" %}
echo "=======Login to wandb (optional)==============="
wandb init
{% endif %}

{% if cookiecutter.venv_tool == "conda" %}
echo "Do `conda activate ./.venv_{{cookiecutter.project_slug}}` to activate the virtual environment"
{% elif cookiecutter.venv_tool == "virtualenv" %}
echo "Do 'source .venv_{{cookiecutter.project_slug}}/bin/activate' to load the enviroment."
{% endif %}

set +xeuo
unset CONDA_ALWAYS_YES
