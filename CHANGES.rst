Changelog
=========


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
