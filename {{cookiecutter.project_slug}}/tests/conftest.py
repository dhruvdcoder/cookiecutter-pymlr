from pathlib import Path
import pytest

{% if cookiecutter.use_tango == 'y' %}
from tango.common.util import (
    find_integrations,
    import_extra_module,
    import_module_and_submodules,
)
import_module_and_submodules("{{cookiecutter.project_slug}}")
{% endif %}

@pytest.fixture
def root_dir():
    return Path(__file__).parent.parent

@pytest.fixture
def data_dir(root_dir):
    return root_dir / "data"
