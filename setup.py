# -*- coding: utf-8 -*-
"""Installer for the imio.smartweb.common package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="imio.smartweb.common",
    version="1.2.38",
    description="Common utilities, vocabularies, taxonomies for imio.smartweb & co products",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: 6.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="iMio",
    author_email="christophe.boulanger@imio.be",
    url="https://github.com/imio/imio.smartweb.common",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/imio.smartweb.common",
        "Source": "https://github.com/imio/imio.smartweb.common",
        "Tracker": "https://github.com/imio/imio.smartweb.common/issues",
        # 'Documentation': 'https://imio.smartweb.common.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["imio", "imio.smartweb"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "setuptools",
        "z3c.jbot",
        "z3c.unconfigure",
        "beautifulsoup4",
        "geopy",
        "Products.GenericSetup>=1.8.2",
        "plone.api>=1.8.4",
        "plone.restapi",
        "plone.app.dexterity",
        "plone.app.imagecropping",
        "plone.app.lockingbehavior",
        "plone.formwidget.geolocation",
        "plone.schema",
        "eea.facetednavigation",
        "imio.gdpr",
        "collective.privacy",
        "collective.taxonomy",
        "iaweb.privacy",
        "imio.smartweb.locales",
        "more-itertools",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.robotframework[debug]",
            "plone.restapi[test]",
            "freezegun",
            "mock",
        ],
    },
    entry_points="""""",
)
