1. Clone the repository

2. Refer the README to install the requirements and download the data

3. Install dev requirements

```bash
pip install -r dev_requirements.txt && pip install -r lint_requirements.txt && pip install -r test_requirements.txt
```

3. Create your branch and write awesome code!

{% if cookiecutter.use_nox == 'y' -%}
4. Run local checks and make sure that everything passes

```
nox --verbose -s pre-commit tests
```
{% endif %}
{% if cookiecutter.use_pre_commit == 'y' -%}
5. Install `pre-commit` to run on all commits.

```
pre-commit install
```
{% endif %}

5. Create a pull request and push your changes for review.
