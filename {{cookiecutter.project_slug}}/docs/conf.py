
import sys
import os

sys.path.insert(0, os.path.abspath("../src"))

extensions = [
    "autoapi.extension",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
    "sphinx_click",
    "m2r",
    "aafigure.sphinxext"
]
source_suffix = [".rst", ".md"]
html_last_updated_fmt = "%c"
master_doc = "index"
project = "{{ cookiecutter.project_name }}"
copyright = "{{ cookiecutter.created.split('-')[0] }}, {{ cookiecutter.project_org }}"
exclude_patterns = ["_build", "docs", "**/docs"]
html_theme = "alabaster"
pygments_style = "friendly"


html_logo = "static/images/logo.png"
html_theme_options = {
    "github_user": "{{ cookiecutter.github_username }}",
    "github_repo": "{{ cookiecutter.github_repo }}",
    "github_banner": True,
    "github_button": True,
    "description": "{{ cookiecutter.project_description }}",
    "fixed_sidebar": True,
}

#html_extra_path = ['../docs/static']
#html_css_files = ['../custom_t.css']
add_module_names = False


# API Generation
autoapi_dirs = ["../src/{{ cookiecutter.project_slug }}"]
autoapi_root = "."
autoapi_options = [
    "members",
    "inherited-members",
    "undoc-members",
    "show-inheritance",
    #"show-module-summary",
]
autoapi_add_toctree_entry = True
autoapi_keep_files = False
autoapi_template_dir = "autoapi_templates"


html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "relations.html",
        "searchbox.html",
        "versioning.html",
    ]
}
