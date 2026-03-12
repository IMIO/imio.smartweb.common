# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`imio.smartweb.common` is a Plone 6 add-on package (namespace: `imio.smartweb.common`) that provides shared utilities, behaviors, REST endpoints, and UI components used across the iMio Smartweb CMS platform.

- **Plone versions:** 6.0, 6.1
- **Python:** 3.10+ (actively tested on 3.12, 3.13)
- **Current version:** 1.2.46.dev0

## Common Commands

```bash
# Bootstrap the development environment (first time)
make buildout

# Run all tests
make test

# Run tests with coverage
./bin/test-coverage

# Run a single test file
./bin/test -s imio.smartweb.common -t test_utils

# Run a single test method
./bin/test -s imio.smartweb.common -t TestUtils.test_geocode_object

# Start the Plone instance (port 8080, admin:admin)
make start

# Clean build artifacts
make cleanall
```

## Architecture

### Package Structure

The source lives in `src/imio/smartweb/common/` (namespace package). Entry point is `configure.zcml` which loads 13 sub-configurations for behaviors, browser, faceted navigation, IA (intelligent agents), REST, serializers, sharing, upgrades, and viewlets.

**Key modules:**
- `config.py` — Constants: `DESCRIPTION_MAX_LENGTH`, `VOCABULARIES_MAPPING`, `IPA_URL`, `APPLICATION_ID`
- `utils.py` — Core utilities: geocoding, vocabulary helpers, image crop validation, environment detection (`is_staging_or_local()`), parent traversal
- `interfaces.py` — Zope interfaces: `IImioSmartwebCommonLayer`, `IAddress`, `ICropping`, etc.
- `vocabularies.py` — Vocabulary factories: Topics, IAm, Countries (locale-aware), Cities (registry-based)
- `indexers.py` — Catalog indexers: `breadcrumb` (full path with titles), `has_leadimage`

**Behaviors** (`behaviors/`): Dexterity behaviors for Topics and IAm fields, registered via ZCML.

**Browser** (`browser/`):
- `forms.py` — Transforms tabs into fieldsets for add/edit forms
- `tiny/process.py` — TinyMCE configuration with accessibility endpoint (`make_accessible`)
- `privacy/` — Cookie consent/GDPR management views
- `overrides/` — Template overrides via z3c.jbot

**REST API** (`rest/`):
- `search_filters.py` — `@search-filters` endpoint: returns available vocabulary terms from a search result set
- `endpoint.py` — `@find` endpoint: advanced search with content type analysis
- `odwb.py` — ODWB (Open Data) integration (disabled in staging/preprod via `is_staging_or_local()`)
- `vocabularies/` — REST vocabulary endpoints

**IA** (`ia/`): Intelligent agent categorization support with custom widgets (HTML snippet, suggested titles).

### Plone/Zope Conventions

- All components registered via ZCML (Zope Component Architecture)
- Use `IImioSmartwebCommonLayer` browser layer for conditional registration
- GenericSetup profiles in `profiles/default/` (install), `profiles/uninstall/`, `profiles/testing/`
- Upgrade steps in `upgrades/` — triggered by GenericSetup on version bump
- Message factory from `imio.smartweb.locales`

### Testing

Tests live in `src/imio/smartweb/common/tests/`. Test infrastructure:
- Layer: `ImioSmartwebCommonLayer` (extends `PLONE_APP_CONTENTTYPES_FIXTURE`)
- Base class: `ImioSmartwebCommonTestCase`
- Three modes: integration, functional, acceptance (Robot Framework)
- Minimum coverage: **90%**
- Timezone forced to UTC during tests

### Buildout

`buildout.cfg` symlinks to `buildout-6.1.cfg` (current default). For Plone 6.0 work, use `buildout-6.0.cfg` explicitly.
