Development and Contributing
============================

The development of python-for-android is managed by the Kivy team `via
Github <https://github.com/kivy/python-for-android>`_.

Issues and pull requests are welcome via the integrated `issue tracker
<https://github.com/kivy/python-for-android/issues>`_.

Read on for more information about how we manage development and
releases, but don't worry about the details! Pull requests are welcome
and we'll deal with the rest.

Development model
-----------------

python-for-android is developed using the following model::

- The ``master`` branch always represents the latest stable release.
- The ``develop`` branch is the most up to date with new contributions.
- Releases happen periodically, and consist of merging the current ``develop`` branch into ``master``.

For reference, this is based on a `Git flow
<https://nvie.com/posts/a-successful-git-branching-model/>`__ model,
although we don't follow this religiously.

Versioning
----------

python-for-android releases currently use `calendar versioning
<https://calver.org/>`__. Release numbers are of the form
YYYY.MM.DD. We aim to create a new release every four weeks, but more
frequent releases are also possible.

We use calendar versioning because in practice, changes in
python-for-android are often driven by updates or adjustments in the
Android build tools. It's usually best for users to be working from
the latest release. We try to maintain backwards compatibility even
while internals are changing.


Creating a new release
----------------------

New releases follow these steps:

- Create a new branch ``release/YYYY.MM.DD`` based on the ``develop`` branch.
  - ``git checkout -b release/YYYY.MM.DD develop``
- Create a Github pull request to merge ``release/YYYY.MM.DD`` into ``master``.
- Complete all steps in the `release checklist <release_checklist_>`_,
  and document this in the pull request (copy the checklist into the PR text)

At this point, wait for reviewer approval and conclude any discussion that arises. To complete the release:

- Merge the release branch to the ``master`` branch.
- Also merge the release branch to the ``develop`` branch.
- Tag the release commit in ``master``. Include a short summary of the changes.
- Create the release distributions: ``python3 setup.py sdist``
- Upload the release to pypi: ``python3 -m twine upload``.
- Upload the release ``.tar.gz`` to the Github tag.

.. _release_checklist:

Release checklist
~~~~~~~~~~~~~~~~~

- [ ] Check that the [build is passing](https://travis-ci.org/kivy/python-for-android)
- [ ] Run the tests locally via `tox`: this performs some long-running tests that are skipped on Travis.
- [ ] Build and run the [on_device_unit_tests](https://github.com/kivy/python-for-android/tree/master/testapps/on_device_unit_tests) app using buildozer. Check that they all pass.
- [ ] Build and run the following [testapps](https://github.com/kivy/python-for-android/tree/master/testapps) for arch `armeabi-v7a` and `arm64-v8a`:
  - [ ] `python3 setup_testapp_python3_sqlite_openssl.py apk`
  - [ ] `python3 setup_testapp_python2.py apk`
- [ ] Check that the version number is correct
