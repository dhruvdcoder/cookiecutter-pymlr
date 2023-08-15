from typing import List
from setuptools import setup, find_packages
import os

# References:
#   1. AllenNLP: https://github.com/allenai/allennlp/blob/main/setup.py
#   2. audreyfeldro/cookiecutter-pypackage

# PEP0440 compatible formatted version, see:
# https://www.python.org/dev/peps/pep-0440/
#
# release markers:
#   X.Y
#   X.Y.Z   # For bugfix releases
#
# pre-release markers:
#   X.YaN   # Alpha release
#   X.YbN   # Beta release
#   X.YrcN  # Release Candidate
#   X.Y     # Final release

# version.py defines the VERSION and VERSION_SHORT variables.
# We use exec here so we don't import package whilst setting up.

VERSION = {}  # type: ignore
with open("src/{{ cookiecutter.project_slug }}/version.py", "r") as version_file:
    exec(version_file.read(), VERSION)


PATH_ROOT = os.path.dirname(__file__)

with open("README.md", "r") as fh:
    long_description = fh.read()


def load_requirements(path_dir: str = PATH_ROOT, comment_char: str = "#") -> List[str]:
    with open(os.path.join(path_dir, "core_requirements.txt"), "r") as file:
        lines = [ln.strip() for ln in file.readlines()]
    reqs = []

    for ln in lines:
        # filer all comments

        if comment_char in ln:
            ln = ln[: ln.index(comment_char)]

        if ln:  # if requirement is not empty
            reqs.append(ln)

    return reqs


install_requires = load_requirements()

setup(
    name="{{ cookiecutter.project_slug }}",
    version=VERSION["VERSION"],
    author="{{ cookiecutter.author.name }}",
    author_email="{{ cookiecutter.author.email }}",
    description="{{ cookiecutter.project_description }}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="{{ cookiecutter.project_url }}",
    project_urls={
        "Documentation": "{{cookiecutter.project_docs_url}}",
        "Source Code": "{{ cookiecutter.project_source_url }}",
    },
    packages=find_packages(
        where="src",
        exclude=[
            "*.tests",
            "*.tests.*",
            "tests.*",
            "tests",
        ],
    ),
    package_dir={"": "src"},
    install_requires=install_requires,
    keywords={{ cookiecutter.keywords.split('|') | string}},
    entry_points={
        "console_scripts": [
            "{{ cookiecutter.project_slug }}={{ cookiecutter.project_slug }}.__main__:main",
        ]
    },
{%- set license_classifiers = {
    'MIT license': 'License :: OSI Approved :: MIT License',
    'BSD license': 'License :: OSI Approved :: BSD License',
    'ISC license': 'License :: OSI Approved :: ISC License (ISCL)',
    'Apache Software License 2.0': 'License :: OSI Approved :: Apache Software License',
    'GNU General Public License v3': 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
} %}
    classifiers=[
        "Programming Language :: Python :: 3",
{% for python_version in cookiecutter.python_versions.requires %}
        "Programming Language :: Python :: {{ python_version }}",
{%- endfor -%}
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
{%- if cookiecutter.license in license_classifiers %}
        "{{ license_classifiers[cookiecutter.open_source_license] }}",
{%- endif %}
    ],

  python_requires=">={{ cookiecutter.python_version}}"

)
