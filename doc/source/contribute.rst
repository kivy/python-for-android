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

python-for-android is developed using the following model:

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

- Create a new branch ``release-YYYY.MM.DD`` based on the ``develop`` branch.
  - ``git checkout -b release-YYYY.MM.DD develop``
- Create a Github pull request to merge ``release-YYYY.MM.DD`` into ``master``.
- Complete all steps in the `release checklist <release_checklist_>`_,
  and document this in the pull request (copy the checklist into the PR text)

At this point, wait for reviewer approval and conclude any discussion that arises. To complete the release:

- Merge the release branch to the ``master`` branch.
- Also merge the release branch to the ``develop`` branch.
- Tag the release commit in ``master``, with tag ``vYYYY.MM.DD``. Include a short summary of the changes.
- Create the release distributions: ``python3 setup.py sdist bdist_wheel``
- Upload the release to pypi: ``python3 -m twine upload``.
- Add to the Github release page (see e.g. `this example <https://github.com/kivy/python-for-android/releases/tag/v2019.06.06>`__):
  - The python-for-android README summary
  - A short list of major changes in this release, if any
  - A changelog summarising merge commits since the last release
  - The release sdist and wheel(s)

.. _release_checklist:

Release checklist
~~~~~~~~~~~~~~~~~

- [ ] Check that the [build is passing](https://travis-ci.org/kivy/python-for-android)
- [ ] Run the tests locally via `tox`: this performs some long-running tests that are skipped on Travis.
- [ ] Build and run the [on_device_unit_tests](https://github.com/kivy/python-for-android/tree/master/testapps/on_device_unit_tests) app using buildozer. Check that they all pass.
- [ ] Build and run the following [testapps](https://github.com/kivy/python-for-android/tree/master/testapps) for arch `armeabi-v7a` and `arm64-v8a`:
  - `python3 setup_testapp_python3_sqlite_openssl.py apk`
    - [ ] `armeabi-v7a`
    - [ ] `arm64-v8a`
  - `python3 setup_testapp_python2.py apk`
    - [ ] `armeabi-v7a`
    - [ ] `arm64-v8a`
- [ ] Check that the version number is correct



How python-for-android uses `pip`
---------------------------------

*Last update: July 2019*

This section is meant to provide a quick summary how
p4a (=python-for-android) uses pip and python packages in
its build process.
**It is written for a python
packagers point of view, not for regular end users or
contributors,** to assist with making pip developers and
other packaging experts aware of p4a's packaging needs.

Please note this section just attempts to neutrally list the
current mechanisms, so some of this isn't necessarily meant
to stay but just how things work inside p4a in
this very moment.


Basic concepts
~~~~~~~~~~~~~~

*(This part repeats other parts of the docs, for the sake of
making this a more independent read)*

p4a builds & packages a python application for use on Android.
It does this by providing a Java wrapper, and for graphical applications
an SDL2-based wrapper which can be used with the kivy UI toolkit if
desired (or alternatively just plain PySDL2). Any such python application
will of course have further library dependencies to do its work.

p4a supports two types of package dependencies for a project:

**Recipe:** install script in custom p4a format. Can either install
C/C++ or other things that cannot be pulled in via pip, or things
that can be installed via pip but break on android by default.
These are maintained primarily inside the p4a source tree by p4a
contributors and interested folks.

**Python package:** any random pip python package can be directly
installed if it doesn't need adjustments to work for Android.

p4a will map any dependency to an internal recipe if present, and
otherwise use pip to obtain it regularly from whatever external source.


Install process regarding packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The install/build process of a p4a project, as triggered by the
`p4a apk` command, roughly works as follows in regards to python
packages:

1. The user has specified a project folder to install. This is either
   just a folder with python scripts and a `main.py`, or it may
   also have a `pyproject.toml` for a more standardized install.

2. Dependencies are collected: they can be either specified via
   ``--requirements`` as a list of names or pip-style URLs, or p4a
   can optionally scan them from a project folder via the
   pep517 library (if there is a `pyproject.toml` or `setup.py`).

3. The collected dependencies are mapped to p4a's recipes if any are
   available for them, otherwise they're kept around as external
   regular package references.

4. All the dependencies mapped to recipes are built via p4a's internal
   mechanisms to build these recipes. (This may or may not indirectly
   use pip, depending on whether the recipe wraps a python package
   or not and uses pip to install or not.)

5. **If the user has specified to install the project in standardized
   ways,** then the `setup.py`/whatever build system
   of the project will be run. This happens with cross compilation set up
   (`CC`/`CFLAGS`/... set to use the
   proper toolchain) and a custom site-packages location.
   The actual comand is a simple `pip install .` in the project folder
   with some extra options: e.g. all dependencies that were already
   installed by recipes will be pinned with a `-c` constraints file
   to make sure pip won't install them, and build isolation will be
   disabled via ``--no-build-isolation`` so pip doesn't reinstall
   recipe-packages on its own.

   **If the user has not specified to use standardized build approaches**,
   p4a will simply install all the remaining dependencies that weren't
   mapped to recipes directly and just plain copy in the user project
   without installing. Any `setup.py` or `pyproject.toml` of the user
   project will then be ignored in this step.

6. Google's gradle is invoked to package it all up into an `.apk`.


Overall process / package relevant notes for p4a
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here are some common things worth knowing about python-for-android's
dealing with python packages:

- Packages will work fine without a recipe if they would also build
  on Linux ARM, don't use any API not available in the NDK if they
  use native code, and don't use any weird compiler flags the toolchain
  doesn't like if they use native code. The package also needs to
  work with cross compilation.

- There is currently no easy way for a package to know it is being
  cross-compiled (at least that we know of) other than examining the
  `CC` compiler that was set, or that it is being cross-compiled for
  Android specifically. If that breaks a package it currently needs
  to be worked around with a recipe.

- If a package does **not** work, p4a developers will often create a
  recipe instead of getting upstream to fix it because p4a simply
  is too niche.

- Most packages without native code will just work out of the box.
  Many with native code tend not to, especially if complex, e.g. numpy.

- Anything mapped to a p4a recipe cannot be just reinstalled by pip,
  specifically also not inside build isolation as a dependency.
  (It *may* work if the patches of the recipe are just relevant
  to fix runtime issues.)
  Therefore as of now, the best way to deal with this limitation seems
  to be to keep build isolation always off.


Ideas for the future regarding packaging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- We in overall prefer to use the recipe mechanism less if we can.
  In overall the recipes are just a collection of workarounds.
  It may look quite hacky from the outside, since p4a
  version pins recipe-wrapped packages usually to make the patches reliably
  apply. This creates work for the recipes to be kept up-to-date, and
  obviously this approach doesn't scale too well. However, it has ended
  up as a quite practical interims solution until better ways are found.

- Obviously, it would be nice if packages could know they are being
  cross-compiled, and for Android specifically. We aren't currently aware
  of a good mechanism for that.

- If pip could actually run the recipes (instead of p4a wrapping pip and
  doing so) then this might even allow build isolation to work - but
  this might be too complex to get working. It might be more practical
  to just gradually reduce the reliance on recipes instead and make
  more packages work out of the box. This has been done e.g. with
  improvements to the cross-compile environment being set up automatically,
  and we're open for any ideas on how to improve this.

