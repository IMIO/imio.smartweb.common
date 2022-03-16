Changelog
=========


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
