# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Setup

1. Clone repository with recursive. 

```
git clone --recurse-submodules https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.github_repo}}
```

1. Create an new environment using conda.

```
export CONDA_ALWAYS_YES="true"
conda create -p ./.venv_{{cookiecutter.project_slug}} python=3.9.7 pip
conda init --all
bashrc="$HOME/.bashrc"
bash_profile="$HOME/.bash_profile"

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
echo "activating conda"
conda activate ./.venv_{{cookiecutter.project_slut}}
echo "activated conda"
```

2. Install the dependencies

```
git 
pip install -e .
pip install -r doc_requirements.txt
pip install -r lint_requirements.txt
```

## Downloading datasets
