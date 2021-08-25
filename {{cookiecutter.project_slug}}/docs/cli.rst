Command Line Interface
==================================

Command line interface for the {{ cookiecutter.project_name }}.


{% if cookiecutter.command_line_interface == "Click" }}
.. click:: {{ cookiecutter.project_slug }}.__main__:cli
  :prog: {{ cookiecutter.project_slug }}
  :nested: full
{% endif %}
