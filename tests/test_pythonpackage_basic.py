"""
ONLY BASIC TEST SET. The additional ones are in test_pythonpackage.py.

These are in a separate file because these were picked to run in github-actions,
while the other additional ones aren't (for build time reasons).
"""

import os
import shutil
import sys
import subprocess
import tempfile
import textwrap
from unittest import mock

from pythonforandroid.pythonpackage import (
    _extract_info_from_package,
    get_dep_names_of_package,
    get_package_name,
    _get_system_python_executable,
    is_filesystem_path,
    parse_as_folder_reference,
    transform_dep_for_pip,
)


def local_repo_folder():
    return os.path.abspath(os.path.join(
        os.path.dirname(__file__), ".."
    ))


def fake_metadata_extract(dep_name, output_folder, debug=False):
    # Helper function to write out fake metadata.
    with open(os.path.join(output_folder, "METADATA"), "w") as f:
        f.write(textwrap.dedent("""\
            Metadata-Version: 2.1
            Name: testpackage
            Version: 0.1
            Requires-Dist: testpkg
            Requires-Dist: testpkg2

            Lorem Ipsum"""
        ))
    with open(os.path.join(output_folder, "metadata_source"), "w") as f:
        f.write(u"wheel")  # since we have no pyproject.toml


def test__extract_info_from_package():
    import pythonforandroid.pythonpackage  # noqa
    with mock.patch("pythonforandroid.pythonpackage."
                    "extract_metainfo_files_from_package",
                    fake_metadata_extract):
        assert _extract_info_from_package(
            "whatever", extract_type="name"
        ) == "testpackage"
        assert set(_extract_info_from_package(
            "whatever", extract_type="dependencies"
        )) == {"testpkg", "testpkg2"}


def test_get_package_name():
    # TEST 1 from external ref
    with mock.patch("pythonforandroid.pythonpackage."
                    "extract_metainfo_files_from_package",
                    fake_metadata_extract):
        assert get_package_name("TeStPackaGe") == "testpackage"

    # TEST 2 from a local folder, for which we'll create a fake package:
    temp_d = tempfile.mkdtemp(prefix="p4a-pythonpackage-test-tmp-")
    try:
        with open(os.path.join(temp_d, "setup.py"), "w") as f:
            f.write(textwrap.dedent("""\
                from setuptools import setup
                setup(name="testpackage")
                """
            ))
        pkg_name = get_package_name(temp_d)
        assert pkg_name == "testpackage"
    finally:
        shutil.rmtree(temp_d)


def test_get_dep_names_of_package():
    # TEST 1 from external ref:
    # Check that colorama is returned without the install condition when
    # just getting the names (it has a "; ..." conditional originally):
    dep_names = get_dep_names_of_package("python-for-android")
    assert "colorama" in dep_names
    assert "setuptools" not in dep_names
    try:
        dep_names = get_dep_names_of_package(
            "python-for-android", include_build_requirements=True,
            verbose=True,
        )
    except NotImplementedError as e:
        # If python-for-android was fetched as wheel then build requirements
        # cannot be obtained (since that is not implemented for wheels).
        # Check for the correct error message:
        assert "wheel" in str(e)
        # (And yes it would be better to do a local test with something
        #  that is guaranteed to be a wheel and not remote on pypi,
        #  but that might require setting up a full local pypiserver.
        #  Not worth the test complexity for now, but if anyone has an
        #  idea in the future feel free to replace this subtest.)
    else:
        # We managed to obtain build requirements!
        # Check setuptools is in here:
        assert "setuptools" in dep_names

    # TEST 2 from local folder:
    assert "colorama" in get_dep_names_of_package(local_repo_folder())

    # Now test that exact version pins are kept, but others aren't:
    test_fake_package = tempfile.mkdtemp()
    try:
        with open(os.path.join(test_fake_package, "setup.py"), "w") as f:
            f.write(textwrap.dedent("""\
            from setuptools import setup

            setup(name='fakeproject',
                  description='fake for testing',
                  install_requires=['buildozer==0.39',
                                    'python-for-android>=0.5.1'],
            )
            """))
        # See that we get the deps with the exact version pin kept but
        # the other version restriction gone:
        assert set(get_dep_names_of_package(
            test_fake_package, recursive=False,
            keep_version_pins=True, verbose=True
        )) == {"buildozer==0.39", "python-for-android"}

        # Make sure we also can get the fully cleaned up variant:
        assert set(get_dep_names_of_package(
            test_fake_package, recursive=False,
            keep_version_pins=False, verbose=True
        )) == {"buildozer", "python-for-android"}

        # Test with build requirements included:
        dep_names = get_dep_names_of_package(
            test_fake_package, recursive=False,
            keep_version_pins=False, verbose=True,
            include_build_requirements=True
            )
        assert len(
            {"buildozer", "python-for-android", "setuptools"}.intersection(
                dep_names
            )
        ) == 3  # all three must be included
    finally:
        shutil.rmtree(test_fake_package)


def test_transform_dep_for_pip():
    # A reminder, this entire function we test here is just a workaround
    # for https://github.com/pypa/pip/issues/6097 (and not a nice one.)
    # As soon as upstream fixes it, we should throw it & this test out
    transformed = (
        transform_dep_for_pip(
            "python-for-android @ https://github.com/kivy/" +
            "python-for-android/archive/master.zip"
        ),
        transform_dep_for_pip(
            "python-for-android @ https://github.com/kivy/" +
            "python-for-android/archive/master.zip" +
            "#egg=python-for-android-master"
        ),
        transform_dep_for_pip(
            "python-for-android @ https://github.com/kivy/" +
            "python-for-android/archive/master.zip" +
            "#"  # common hack variant used by others to make pip parse it
        ),
    )
    expected = (
        "https://github.com/kivy/python-for-android/archive/master.zip" +
        "#egg=python-for-android"
    )
    assert transformed == (expected, expected, expected)
    assert transform_dep_for_pip("https://a@b/") == "https://a@b/"


def test_is_filesystem_path():
    assert is_filesystem_path("/some/test")
    assert not is_filesystem_path("https://blubb")
    assert not is_filesystem_path("test @ bla")
    assert is_filesystem_path("/abc/c@d")
    assert not is_filesystem_path("https://user:pw@host/")
    assert is_filesystem_path(".")
    assert is_filesystem_path("")


def test_parse_as_folder_reference():
    assert parse_as_folder_reference("file:///a%20test") == "/a test"
    assert parse_as_folder_reference("https://github.com") is None
    assert parse_as_folder_reference("/a/folder") == "/a/folder"
    assert parse_as_folder_reference("test @ /abc") == "/abc"
    assert parse_as_folder_reference("test @ https://bla") is None


class TestGetSystemPythonExecutable():
    """ This contains all tests for _get_system_python_executable().

    ULTRA IMPORTANT THING TO UNDERSTAND: (if you touch this)

    This code runs things with other python interpreters NOT in the tox
    environment/virtualenv.
    E.g. _get_system_python_executable() is outside in the regular
    host environment! That also means all dependencies can be possibly
    not present!

    This is kind of absurd that we need this to run the test at all,
    but we can't test this inside tox's virtualenv:
    """

    def test_basic(self):
        # Tests function inside tox env with no further special setup.

        # Get system-wide python bin:
        pybin = _get_system_python_executable()

        # The python binary needs to match our major version to be correct:
        pyversion = subprocess.check_output([
            pybin, "-c", "import sys; print(sys.version)"
        ], stderr=subprocess.STDOUT).decode("utf-8", "replace")
        assert pyversion.strip() == sys.version.strip()

    def run__get_system_python_executable(self, pybin):
        """ Helper function to run our function.

            We want to see what _get_system_python_executable() does given
            a specific python, so we need to make it import it and run it,
            with that TARGET python, which this function does.
        """
        cmd = [
            pybin,
            "-c",
            "import importlib\n"
            "import build.util\n"
            "import os\n"
            "import sys\n"
            "sys.path = [os.path.dirname(sys.argv[1])] + sys.path\n"
            "m = importlib.import_module(\n"
            "    os.path.basename(sys.argv[1]).partition('.')[0]\n"
            ")\n"
            "print(m._get_system_python_executable())",
            os.path.join(os.path.dirname(__file__), "..",
                         "pythonforandroid", "pythonpackage.py"),
        ]
        # Actual call to python:
        try:
            return subprocess.check_output(
                cmd, stderr=subprocess.STDOUT
            ).decode("utf-8", "replace").strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError("call failed, with output: " + str(e.output))

    def test_systemwide_python(self):
        # Get system-wide python bin seen from here first:
        pybin = _get_system_python_executable()
        # (this call was not a test, we really just need the path here)

        # Check that in system-wide python, the system-wide python is returned:
        # IMPORTANT: understand that this runs OUTSIDE of any virtualenv.
        try:
            p1 = os.path.normpath(
                self.run__get_system_python_executable(pybin)
            )
            p2 = os.path.normpath(pybin)
            assert p1 == p2
        except RuntimeError as e:
            # (remember this is not in a virtualenv)
            # Some deps may not be installed, so we just avoid to raise
            # an exception here, as a missing dep should not make the test
            # fail.
            if "build" in str(e.args):
                # System python probably doesn't have build available!
                pass
            elif "toml" in str(e.args):
                # System python probably doesn't have toml available!
                pass
            else:
                raise

    def test_venv(self):
        """ Verifies that _get_system_python_executable() works correctly
            in a 'venv' (Python 3 only feature).
        """

        # Get system-wide python bin seen from here first:
        pybin = _get_system_python_executable()
        # (this call was not a test, we really just need the path here)

        test_dir = tempfile.mkdtemp()
        try:
            # Check that in a venv/pyvenv, the system-wide python is returned:
            subprocess.check_output([
                pybin, "-m", "venv", "--",
                os.path.join(test_dir, "venv")
            ])
            subprocess.check_output([
                os.path.join(test_dir, "venv", "bin", "pip"),
                "install", "-U", "pip"
            ])
            subprocess.check_output([
                os.path.join(test_dir, "venv", "bin", "pip"),
                "install", "-U", "build", "toml", "sh<2.0", "colorama",
                "appdirs", "jinja2", "packaging"
            ])
            sys_python_path = self.run__get_system_python_executable(
                os.path.join(test_dir, "venv", "bin", "python")
            )
            assert os.path.normpath(sys_python_path).startswith(
                os.path.normpath(pybin)
            )
        finally:
            shutil.rmtree(test_dir)
