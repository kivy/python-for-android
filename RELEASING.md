# Releasing python-for-android

This document describes the release process for python-for-android. It is
intended for core developers who cut new releases. Casual contributors do
not need to read it.

## Versioning

python-for-android uses [calendar versioning](https://calver.org/) of the
form `YYYY.MM.DD` (e.g. `2026.05.09`). Calendar versioning is used because
changes are often driven by Android build-tool updates, so users generally
want the latest release. Backward compatibility is preserved across
releases where possible.

The single source of truth for the version is
[`pythonforandroid/__init__.py`](pythonforandroid/__init__.py). `setup.py`
parses `__version__` from that file and exposes it as the package version.

## Branching model

- `master` always represents the latest stable release.
- `develop` is the active development branch and the target for all PRs.
- Release branches `release-YYYY.MM.DD` are cut from `develop` for each
  release, then merged into both `master` and back into `develop`.

## Release steps

1. **Cut a release branch** from an up-to-date `develop`:

   ```bash
   git checkout develop && git pull
   git checkout -b release-YYYY.MM.DD
   ```

2. **Bump the version** in
   [`pythonforandroid/__init__.py`](pythonforandroid/__init__.py).

3. **Regenerate `CHANGELOG.md`** using
   [`github-changelog-generator`](https://github.com/github-changelog-generator/github-changelog-generator).

4. **Open a pull request** from `release-YYYY.MM.DD` targeting `master`.
   Copy the [release checklist](#release-checklist) into the PR
   description and tick items off as they are validated.

5. **Wait for review and complete the checklist** before merging.

6. **Merge the release branch into `master`**, then merge it back into
   `develop` so the version bump and changelog land on both branches.

7. **Tag the release commit on `master`** with an annotated tag:

   ```bash
   git checkout master && git pull
   git tag -a vYYYY.MM.DD -m "Release YYYY.MM.DD"
   git push origin vYYYY.MM.DD
   ```

   Tags follow the format `vYYYY.MM.DD`.

8. **PyPI upload happens automatically** when the tag is pushed. The
   [`pypi-release.yml`](.github/workflows/pypi-release.yml) workflow
   builds `sdist` and `bdist_wheel`, runs `twine check`, and uploads via
   the `pypi_password` token. Non-tag pushes still build and check the
   artifacts but do not publish.

9. **Create the GitHub Release** at
   <https://github.com/kivy/python-for-android/releases> from the new
   tag. Use GitHub's "Generate release notes" feature to auto-fill the
   title and description from merged PRs since the previous tag, then
   tweak as needed.

10. **Announce the release on Discord** in the
    [#announcements](https://discord.com/channels/423249981340778496/490505571271704577)
    channel. Include the version number and a link to the GitHub
    release page.

## Release checklist

Use this as the PR description for the release branch.

- [ ] Check that the builds are passing
  - [ ] [GitHub Action](https://github.com/kivy/python-for-android/actions)
- [ ] Run the tests locally via `tox`: this performs some long-running tests that are skipped on github-actions.
- [ ] Build and run the [on_device_unit_tests](https://github.com/kivy/python-for-android/tree/master/testapps/on_device_unit_tests) app using buildozer. Check that they all pass.
- [ ] Build (or download from github actions) and run the following [testapps](https://github.com/kivy/python-for-android/tree/master/testapps/on_device_unit_tests) for arch `armeabi-v7a` and `arm64-v8a`:
  - [ ] on_device_unit_tests
    - [ ] `armeabi-v7a` (`cd testapps/on_device_unit_tests && PYTHONPATH=.:../../ python3 setup.py apk  --ndk-dir=<your-ndk-dir> --sdk-dir=<your-sdk-dir> --arch=armeabi-v7a --debug`)
    - [ ] `arm64-v8a` (`cd testapps/on_device_unit_tests && PYTHONPATH=.:../../ python3 setup.py apk  --ndk-dir=<your-ndk-dir> --sdk-dir=<your-sdk-dir> --arch=arm64-v8a --debug`)
- [ ] Check that the version number is correct
