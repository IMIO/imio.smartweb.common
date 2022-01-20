.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image:: https://github.com/IMIO/imio.smartweb.common/workflows/Tests/badge.svg
    :target: https://github.com/IMIO/imio.smartweb.common/actions?query=workflow%3ATests
    :alt: CI Status

.. image:: https://coveralls.io/repos/github/IMIO/imio.smartweb.common/badge.svg?branch=main
    :target: https://coveralls.io/github/IMIO/imio.smartweb.common?branch=main
    :alt: Coveralls

.. image:: https://img.shields.io/pypi/v/imio.smartweb.common.svg
    :target: https://pypi.python.org/pypi/imio.smartweb.common/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/imio.smartweb.common.svg
    :target: https://pypi.python.org/pypi/imio.smartweb.common
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/imio.smartweb.common.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/imio.smartweb.common.svg
    :target: https://pypi.python.org/pypi/imio.smartweb.common/
    :alt: License


====================
imio.smartweb.common
====================

Provides various common needs for smartweb related sites :

- topics field behavior with topics vocabulary select widget
- Iam field behavior with "iam" vocabulary select widget
- rich description feature, with bold & newlines, limited to a maximum of chars (see ``config.py``)
- countries vocabulary
- cities vocabulary (values are stored in registry)
- faceted relative path widget
- ``breadcrumb`` index that stores the full object path with titles (and not ids)
- ``has_leadimage`` index that stores if there is a lead_image on the object or not
- cropping scales selection mechanism per content-type / field (with adapters)
- help texts (descriptions) on forms above the fields and not below
- ``@search-filter`` REST endpoint to get all terms (and titles) of metadatas from search request results
- colophon viewlet override to add legal mention, accessibility info, cookies preferences & copyright
- cookies opt-in support for analytics and iframes (Accept/Refuse all or detailed preferences)


Custom Add / Edit forms are also provided to :

- Transform tabs into expandable fieldsets
- Hide lead image caption field (never used)


Utils fonctions are also provided for :

- vocabulary term translation
- object geolocation (with ``IAddress`` schema)


A (very) simplified TinyMCE configuration is also made.


Translations
------------

This product has been translated into

- French


Installation
------------

Install imio.smartweb.common by adding it to your buildout::

    [buildout]

    ...

    eggs =
        imio.smartweb.common


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/imio/imio.smartweb.common/issues
- Source Code: https://github.com/imio/imio.smartweb.common


License
-------

The project is licensed under the GPLv2.
