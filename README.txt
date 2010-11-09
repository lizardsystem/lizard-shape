lizard-shape
==========================================

Introduction


Usage
-----

- Add lizard_shape to your buildout.cfg.

- Add lizard_shape and lizard_map to the INSTALLED_APPS in your
  settings.

- Add app in your urls.py, i.e. (r'^shape/', include('lizard_shape.urls')).

- Add a link to the app somewhere:

    - {% url lizard_shape.homepage %} in a template

    - reverse('lizard_shape.homepage')

- Optionally set MAP_SETTINGS, DEFAULT_START_DAYS and DEFAULT_END_DAYS
  in your settings. See the lizard_map testsettings for examples.

Make the database tables:

    $> bin/django syncdb

- Add some data in the admin screen.


Development installation
------------------------

The first time, you'll have to run the "bootstrap" script to set up setuptools
and buildout::

    $> python bootstrap.py

And then run buildout to set everything up::

    $> bin/buildout

(On windows it is called ``bin\buildout.exe``).

You'll have to re-run buildout when you or someone else made a change in
``setup.py`` or ``buildout.cfg``.

The current package is installed as a "development package", so
changes in .py files are automatically available (just like with ``python
setup.py develop``).

If you want to use trunk checkouts of other packages (instead of released
versions), add them as an "svn external" in the ``local_checkouts/`` directory
and add them to the ``develop =`` list in buildout.cfg.

Tests can always be run with ``bin/test`` or ``bin\test.exe``.
