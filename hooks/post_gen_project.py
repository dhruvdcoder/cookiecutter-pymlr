import os
import sys

"""Remove conditional files and folders after creation"""

REMOVE_PATHS = [
    '{% if cookiecutter.use_vscode != "y" %} .vscode, {% endif %}',
    '{% if cookiecutter.use_umass_clusters != "y" %} .vscode/sftp.json, {% endif %}'
]

for path in REMOVE_PATHS:
    path = path.strip()
    if path and os.path.exists(path):
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.unlink(path)