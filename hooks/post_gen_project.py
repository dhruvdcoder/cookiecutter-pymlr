import os
import shutil

"""Remove conditional files and folders after creation"""

REMOVE_PATHS = (
    '{% if cookiecutter.use_vscode != "y" %} .vscode, {% endif %}'
    '{% if cookiecutter.use_umass_clusters != "y" %} .vscode/sftp.json, {% endif %}'
    '{% if cookiecutter.use_nox != "y" %} noxfile.py, {% endif %}'
    '{% if cookiecutter.use_pre_commit != "y" %} .pre-commit-config.yaml, {% endif %}'
    '{% if cookiecutter.use_pytest != "y" %} tests, {% endif %}'
    '{% if cookiecutter.use_github_actions != "y" %} .github, CHANGELOG.md, CONTRIBUTING.md, {% endif %}'
    '{% if cookiecutter.use_docs != "y" %} docs, doc_requirements.txt {% endif %}'
)

print("Removing conditional files and folders after creation")
print(f"REMOVE_PATHS: {REMOVE_PATHS}")
for path in REMOVE_PATHS.split(","):
    path = path.strip()
    if path and os.path.exists(path):
        print(f"Removing directory {path}")
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            print(f"Removing file {path}")
            os.unlink(path)
    else:
        print(f"Path {path} does not exist")
