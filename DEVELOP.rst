Using the development buildout
==============================

Requires `uv <https://docs.astral.sh/uv/getting-started/installation/>`_.

Create a virtualenv in ``.venv``, install requirements and run buildout::

    $ make buildout

Start Plone in foreground::

    $ make start

List all available targets::

    $ make help


Running tests
-------------

    $ tox

list all tox environments:

    $ tox -l
    py27-Plone43
    py27-Plone51
    py27-Plone52
    py37-Plone52
    build_instance
    code-analysis
    lint-py27
    lint-py37
    coverage-report

run a specific tox env:

    $ tox -e py37-Plone52

