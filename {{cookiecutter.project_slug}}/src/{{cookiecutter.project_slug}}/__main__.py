import logging
import os
import sys
{%- if cookiecutter.command_line_interface=="Click" %}
import click
{%- endif %}

{%- if cookiecutter.command_line_interface|lower == 'argparse' %}
import argparse
{%- endif %}

if os.environ.get("{{ cookiecutter.project_slug | upper}}_DEBUG"):
    LEVEL = logging.DEBUG
else:
    level_name = os.environ.get("{{ cookiecutter.project_slug | upper }}_LOG_LEVEL", "INFO")
    LEVEL = logging._nameToLevel.get(level_name, logging.INFO)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(name)s - %(message)s", level=LEVEL)

{% if cookiecutter.command_line_interface|lower == 'click' %}
@click.command()
def main(args=None):
    """Console script for {{cookiecutter.project_slug}}."""
    click.echo("Replace this message by putting your code into "
               "{{cookiecutter.project_slug}}.__main__.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")

    return 0
{%- endif %}
{%- if cookiecutter.command_line_interface|lower == 'argparse' %}
def main():
    """Console script for {{cookiecutter.project_slug}}."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    args = parser.parse_args()

    print("Arguments: " + str(args._))
    print("Replace this message by putting your code into "
          "{{cookiecutter.project_slug}}.__main__.main")

    return 0
{%- endif %}

if __name__ == "__main__":
    main(prog_name="{{cookiecutter.project_name}}")
