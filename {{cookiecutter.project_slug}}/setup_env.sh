#!/bin/bash -i
set -ex

export CONDA_ALWAYS_YES="true"

echo "=======Creating virtual env========="
{% if cookiecutter.venv_tool == "conda" %}

conda create -p ./.venv_{{cookiecutter.project_slug}} python={{cookiecutter.python_version}} pip
conda init --all
bashrc="$HOME/.bashrc"
bash_profile="$HOME/.bash_profile"

set +ex

if [ -f "$bashrc" ]
then
echo "sourcing $bashrc"
source $bashrc
echo "sourced $bashrc"
else
echo "sourcing $bash_profile"
source $bash_profile
echo "sourced $bash_profile"
fi

set -e
echo "activating conda"
conda activate ./.venv_{{cookiecutter.project_slug}}
echo "activated conda"

{% elif cookiecutter.venv_tool == "virtualenv" %}

python3 -m virtualenv  .venv_{{cookiecutter.project_slug}}

source .venv_{{cookiecutter.project_slug}}/bin/activate
{% endif %}

set -x

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

set +x
unset CONDA_ALWAYS_YES
