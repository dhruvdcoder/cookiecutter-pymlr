import os
import sys

"""Remove conditional files and folders after creation"""

REMOVE_PATHS = [
    '{% if cookiecutter.use_vscode != "y" %} .vscode, {% endif %}',
    '{% if cookiecutter.use_umass_clusters != "y" %} .vscode/sftp.json, {% endif %}'
    '{% if cookiecutter.use_nox != "y" %} noxfile.py, {% endif %}',
    '{% if cookiecutter.use_pre_commit != "y" %} .pre-commit-config.yaml, {% endif %}',
    '{% if cookiecutter.use_pytest != "y" %} tests, {% endif %}',
    '{% if cookiecutter.use_github_actions != "y" %} .github, CHANGELOG.md, CONTRIBUTING.md {% endif %}',
    '{% if cookiecutter.use_docs != "y" %} docs, doc_requirements.txt {% endif %}',
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path and os.path.exists(path):
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.unlink(path)