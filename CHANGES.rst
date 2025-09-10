Changelog
=========


1.2.38 (2025-09-10)
-------------------

- @find : Process None value in a field or ["None", "other value"] for agatha stats
  [boulch

- Add plone.app.caching include for futur proofing override
  [jchandelle]


1.2.37 (2025-09-03)
-------------------

- Add new @find endpoint to find content in instance
  [boulch]


1.2.36 (2025-06-25)
-------------------

- WEB-4278 : Create translated (de) iam vocabulary for e-guichet (citizen project)
  [boulch]

- WEB-4278 : Create translated (de) topics vocabulary for e-guichet (citizen project)
  [boulch]

- WEB-4269 : Add Horizontal Rule option to the insert menu in TinyMCE
  [remdub]


1.2.35 (2025-05-26)
-------------------

- CITI-7 : Fix retrieving mimeType for some picture files
  [boulch]


1.2.34 (2025-05-26)
-------------------

- WEB-4258 : Temporary CSS fix to unhide the "External link" tab when adding a new link.
  This a temporary fix while waiting for a new release in imio_smartweb_themes
  [remdub]


1.2.33 (2025-05-22)
-------------------

- WEB-4259 : Override plone.volto summary_serializer_metadata to solve a problem with new
  metadata fields being added to the summary serializer and breaking our search endpoints
  [bsuttor, remdub]


1.2.32 (2025-05-19)
-------------------

- WEB-4250 : Quick fix : Since Plone 6.1, AjaxSelectWidget is displaying in edit mode even if mode is "display"
  [boulch]


1.2.31 (2025-05-15)
-------------------

- Dirty css fix to hide the "Upload" button in the new pat-contentbrowser
  [remdub]


1.2.30 (2025-05-14)
-------------------

- Upgrade missing TinyMCE settings to version 7
  [remdub]


1.2.29 (2025-05-13)
-------------------

- Upgrade TinyMCE settings to version 7
  [remdub]


1.2.28 (2025-04-30)
-------------------

- Upgrade dev environment to Plone 6.1-latest
  [remdub]

- Add tests for Plone 6.1-latest and add Python 3.13
  [remdub]


1.2.27 (2025-03-19)
-------------------

- WEB-4122 : Create adapter/validator to filter valid image mimetype in our solutions
  [boulch]


1.2.26 (2025-03-12)
-------------------

- WEB-4212: Fixe i18n:domain for skip to content
  [thomlamb]


1.2.25 (2025-03-10)
-------------------

- WEB-4232 : Fix JQuery.
  Version 1.2.24 contained issues affecting the smooth running of the preventing deletion of a taxonomy term
  [boulch]


1.2.24 (2025-03-10)
-------------------

- WEB-4232 : Refactoring of the code that prevents the deletion of a taxonomy term if it is used in at least one object
  [boulch]


1.2.23 (2025-02-24)
-------------------

- WEB-3718 : Accessibility : Add aria-label for consent buttons
  [boulch]


1.2.22 (2025-02-14)
-------------------

- WEB-4153 : Ruleset plone.stableResource for image scales
  [remdub]


1.2.21 (2025-01-31)
-------------------

- **Fix:** Updated to align scale behavior with the fix in plone.scale ([commit a352815](https://github.com/plone/plone.scale/commit/a352815#diff-24f46fc714c6d36041bcea7e64a7d5aeceacd929eb802655276a1d8f4b4576f4R209)).
  [boulch]


1.2.20 (2025-01-29)
-------------------

- Update Python classifiers to be compatible with Python 3.12
  [remdub]

- Migrate to Plone 6.0.14
  [boulch]


1.2.19 (2025-01-09)
-------------------

- WEB-4153 : Override @vocabularies endpoint to add a cache ruleset on it
  [remdub]


1.2.18 (2024-07-01)
-------------------

- WEB-4088 : Refactor code for odwb staging availability
  [boulch]

- GHA tests on Python 3.8 3.9 and 3.10
  [remdub]


1.2.17 (2024-06-06)
-------------------

- WEB-4113 : Add `TranslatedAjaxSelectFieldWidget` to fix translations of initial
  values in select2 fields
  [laulaz]


1.2.16 (2024-05-30)
-------------------

- WEB-4107 : Update resource registries modification time (used as ETag) at Zope startup
  [laulaz]


1.2.15 (2024-05-27)
-------------------

- Fix missing ZCML dependency
  [laulaz]


1.2.14 (2024-05-24)
-------------------

- Fix bundles: Remove obsolete patterns bundle and fix a previous upgrade for
  eea.facetednavigation
  [laulaz]

- Fix translate call (was causing incorrect string in .po file)
  [laulaz]

- Fix translation message string
  [laulaz]


1.2.13 (2024-05-24)
-------------------

- WEB-4088 : Cover use case for sending data in odwb for a staging environment
  [boulch]

- Ensure translation of vocabularies when used with `AjaxSelectFieldWidget`
  [laulaz]

- Remove useless `container_uid` from `search-filters` results
  [laulaz]

- WEB-3864 : Ensure that a taxonomy term that is deleted is not used anywhere
  [boulch]

- WEB-3862 : Unpatch (restore original) eea.facetednavigation jquery
  [laulaz]


1.2.12 (2024-05-06)
-------------------

- WEB-4102 : Add second skip to footer
  [thomlamb]


1.2.11 (2024-05-02)
-------------------

- WEB-4101 : Fix vocabulary terms translation (for Topics only - for the moment)
  when used with `AjaxSelectFieldWidget`
  [laulaz]


1.2.10 (2024-05-02)
-------------------

- WEB-4101 : Change Topics field widget to keep value ordering
  [laulaz]

- WEB-4088 : Implement some odwb utils and generic classes
  [boulch]


1.2.9 (2024-02-08)
------------------

- WEB-4064 : Reindex SolR because of changes in schema
  [remdub]


1.2.8 (2024-02-02)
------------------

- Fix skip content sr-only
  [thomlamb]

1.2.7 (2024-01-16)
------------------

- WEB-4046 : Add css for "Skip to content
  [thomlamb]

- WEB-4046 : Add "Skip to content" link for a11y
  [laulaz]

- WEB-4048 : Put focus on cookies accept button for a11y
  [laulaz]


1.2.6 (2024-01-09)
------------------

- WEB-4041 : Add new "carre" scale
  [boulch]


1.2.5 (2024-01-05)
------------------

- WEB-4007 : Get ContactProperties out of imio.smartweb.core to also use it in imio.directory.core
  and simplifying formated schedule displaying in REACT directory view
  [boulch]

- WEB-4029 : File and Image content types don't have WF so we set effective date equal to created date
  [boulch]


1.2.4 (2023-12-07)
------------------

- WEB-3783 : Rebuild url with request.form datas (usefull with react views)
  [boulch]


1.2.3 (2023-11-21)
------------------

- Improve image compression quality
  [laulaz]

- Change portrait scales dimensions
  [laulaz]


1.2.2 (2023-11-20)
------------------

- Fix missing values for facilities lists (causing `None` in REST views filters)
  See https://github.com/collective/collective.solr/issues/366
  [laulaz]

- Fix last upgrade steps: when run from command line, we need to adopt admin
  user to find private objects
  [laulaz]

- WEB-4003 : Fix missing TextField mimetypes
  [laulaz]


1.2.1 (2023-10-29)
------------------

- SUP-33128 : Fix eea.facetednavigation : Hide items with 0 results
  [boulch, laz]

- Refactor less and js compilation + Add compilations files
  [boulch]


1.2 (2023-10-25)
----------------

- WEB-3985 : New portrait / paysage scales & logic.
  We have re-defined the scales & sizes used in smartweb.
  We let the user crop only 2 big portrait / paysage scales and make the calculation behind the scenes for all
  other smaller scales.
  We also fixed the cropping information clearing on images changes.
  [boulch, laulaz]


1.1.9 (2023-08-28)
------------------

- WEB-3974 : Add new registry key (imio.smartweb.common.log) to activate logging in smartweb / auth sources products
  [boulch]

- Fix AttributeError in case of instance behaviors attributes that are not on all objects
  [boulch]


1.1.8 (2023-08-09)
------------------

- WEB-3960 : Clean unhautorized xml chars out of text when added or modified contents
  Temporary patch. Waiting for this fix : https://github.com/plone/plone.app.z3cform/pull/167
  [boulch]

- WEB-3955 : Authentic sources : Crop view on Image type should not return scales
  [boulch]


1.1.7 (2023-05-22)
------------------

- Change banner scale to have infinite height
  [laulaz]

- Migrate to Plone 6.0.4
  [boulch]


1.1.6 (2023-04-14)
------------------

- Don't use image_scales metadata anymore (Fix faceted)
  [boulch, laulaz]

- Update object modification date if cropping was removed/updated
  [boulch, laulaz]


1.1.5 (2023-03-14)
------------------

- WEB-3862 : Patch (Remove select2) eea.facetednavigation jquery
  [laulaz, boulch]


1.1.4 (2023-03-13)
------------------

- Allow to add portal messages when content images are too small for cropping.
  This can be done dynamically on a view call with a single line of code:
  `show_warning_for_scales(self.context, self.request)`
  [laulaz]

- Migrate to Plone 6.0.2
  [boulch]


1.1.3 (2023-02-22)
------------------

- WEB-3852 : Fix atom/syndication registry keys
  [boulch]


1.1.2 (2023-01-30)
------------------

- Call `@@consent-json` view on navigation root (instead of context)
  [laulaz]

- Ensure Ajax requests are always uncached
  [laulaz]


1.1.1 (2023-01-12)
------------------

- Allow to choose language for vocabulary term translation
  [laulaz]

- Use bootstrap dropdown-toggle for fieldsets collapse icon on edit forms
  [laulaz]

- Fix TinyMCE menu bar and format menu
  [laulaz]

- Update `widget.pt` override from `plone.app.z3cform.templates`
  [laulaz]

- Improve monkeypatch to fix TTW resource calling
  [laulaz]

- Update buildout to get Plone 6.0.0 final
  [laulaz]


1.1 (2022-12-20)
----------------

- Add monkeypatch to fix TTW resource calling
  See https://github.com/plone/Products.CMFPlone/issues/3705
  [laulaz]

- Uninstall collective.js.jqueryui
  [boulch]

- Remove faceted deprecated bundles
  [boulch]

- Migrate to Plone 6 : remove dexteritytextindexer, use new simplified
  resources registry, fix TinyMCE configuration and images scales,
  manual minimized js
  [laulaz, boulch]


1.0.10 (2022-11-22)
-------------------

- Ignore batch related query parameters for `search-filters` endpoint
  [laulaz]


1.0.9 (2022-11-15)
------------------

- Add helper method to get language from smartweb REST requests
  This is needed for multilingual authentic sources
  [laulaz]

- Allow to translate vocabulary terms titles in search-filters endpoint
  This is needed for multilingual authentic sources
  [laulaz]


1.0.8 (2022-08-08)
------------------

- MWEB-54 : Update TinyMCE : Add non breaking space option
  [boulch]


1.0.7 (2022-06-13)
------------------

- Add connection link in colophon
  [laulaz]


1.0.6 (2022-06-07)
------------------

- Add ban_physicalpath method (taken from policy)
  [boulch, laulaz]


1.0.5 (2022-05-16)
------------------

- Refactor rich description to retrieve html on a any description
  (from context or from other ways)
  [boulch]


1.0.4 (2022-05-03)
------------------

- Limit uploaded files sizes to 20Mo with JS (without reaching the server)
  [laulaz]

- Add help text on lead image field also on edit forms
  [laulaz]


1.0.3 (2022-05-02)
------------------

- Hide faceted actions
  [boulch]


1.0.2 (2022-04-25)
------------------

- Hide unwanted upgrades from site-creation and quickinstaller
  [boulch]

- Add local manager role and sharing permissions rolemap
  [boulch]

- Add help text on lead image fields
  [boulch]

- Fix privacy views JS calls (sometimes called on Zope root instead of Plone root)
  [laulaz]

- Add Subject keywords to SearchableText index
  [laulaz]


1.0.1 (2022-03-16)
------------------

- Allow readers, editors and reviewers to see inactive (expired) contents
  [laulaz]


1.0 (2022-03-08)
----------------

- Avoid traceback if @@get_analytics is called outside Plone site
  [laulaz]


1.0a11 (2022-02-21)
-------------------

- Load Analytics via JS call to avoid non-privacy aware caching
  [laulaz]

- Change privacy views permissions to zope.Public
  [laulaz]


1.0a10 (2022-02-10)
-------------------

- Hide ical import related actions
  [laulaz]


1.0a9 (2022-02-01)
------------------

- Update buildout to use Plone 6.0.0a3 packages versions
  [boulch]

- Remove unneeded override: it has been included in plone.app.z3c.form
  See https://github.com/plone/plone.app.z3cform/issues/138
  [laulaz]


1.0a8 (2022-01-24)
------------------

- Change colophon copyright position
  [laulaz]

- Change cookies viewlet / overlay logic. We now show (simplified) overlay only
  to see detailed options about cookies because viewlet allows to Accept / Refuse
  all cookies directly
  [laulaz]

- Add Cookies preferences link in colophon
  [laulaz]

- Change some cookies-related texts
  [laulaz]

- Fix iframes transform with existing classes or when there are several iframes
  [laulaz]


1.0a7 (2022-01-19)
------------------

- Update buildout to use Plone 6.0.0a2 released version
  [laulaz]

- Remove portal messages from cookies settings overlay
  [laulaz]


1.0a6 (2022-01-13)
------------------

- Add cookies opt-in support for analytics and iframes
  [laulaz]

- Override colophon viewlet to display legal mention, accessibility info and
  copyright links (dependency on imio.gdpr)
  [laulaz]


1.0a5 (2021-12-16)
------------------

- Fix vocabulary term translation (missing lang)
  [laulaz]


1.0a4 (2021-11-23)
------------------

- Add utility to get a vocabulary
  [boulch]


1.0a3 (2021-11-16)
------------------

- Avoid traceback if configure_faceted is called on non-configured type (ex: on
  default collections at Plone install)
  [laulaz]


1.0a2 (2021-11-05)
------------------

- Fix setup.py classifiers & URLs
  [laulaz]


1.0a1 (2021-11-05)
------------------

- Initial release.
  [boulch]
