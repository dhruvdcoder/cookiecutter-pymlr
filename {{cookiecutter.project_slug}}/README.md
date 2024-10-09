# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Setup

1. Clone repository with recursive. 

```
git clone --recurse-submodules https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.github_repo}}
```

1. Create an new environment using conda.

```
conda create -p ./.venv_{{cookiecutter.project_slug}} python=3.9.7 pip ipykernel
conda activate ./.venv_{{cookiecutter.project_slug}}
```

2. Install the dependencies

```
git 
pip install -e .
```
and the following if you are going to develop on the same code-base

```
pip install -r lint_requirements.txt
pip install -r test_requirements.txt
```

## Downloading datasets
