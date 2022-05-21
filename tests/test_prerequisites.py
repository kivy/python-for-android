import unittest
from unittest import mock, skipIf

import sys

from pythonforandroid.prerequisites import (
    JDKPrerequisite,
    HomebrewPrerequisite,
    OpenSSLPrerequisite,
    AutoconfPrerequisite,
    AutomakePrerequisite,
    LibtoolPrerequisite,
    PkgConfigPrerequisite,
    CmakePrerequisite,
    get_required_prerequisites,
)


class PrerequisiteSetUpBaseClass:
    def setUp(self):
        self.mandatory = dict(linux=False, darwin=False)
        self.installer_is_supported = dict(linux=False, darwin=False)
        self.expected_homebrew_formula_name = ""

    def test_is_mandatory_on_darwin(self):
        assert self.prerequisite.mandatory["darwin"] == self.mandatory["darwin"]

    def test_is_mandatory_on_linux(self):
        assert self.prerequisite.mandatory["linux"] == self.mandatory["linux"]

    def test_installer_is_supported_on_darwin(self):
        assert (
            self.prerequisite.installer_is_supported["darwin"]
            == self.installer_is_supported["darwin"]
        )

    def test_installer_is_supported_on_linux(self):
        assert (
            self.prerequisite.installer_is_supported["linux"]
            == self.installer_is_supported["linux"]
        )

    def test_darwin_pkg_config_location(self):
        self.assertEqual(self.prerequisite.darwin_pkg_config_location(), "")

    def test_linux_pkg_config_location(self):
        self.assertEqual(self.prerequisite.linux_pkg_config_location(), "")

    @skipIf(sys.platform != "darwin", "Only run on macOS")
    def test_pkg_config_location_property__darwin(self):
        self.assertEqual(
            self.prerequisite.pkg_config_location,
            self.prerequisite.darwin_pkg_config_location(),
        )

    @skipIf(sys.platform != "linux", "Only run on Linux")
    def test_pkg_config_location_property__linux(self):
        self.assertEqual(
            self.prerequisite.pkg_config_location,
            self.prerequisite.linux_pkg_config_location(),
        )


class TestJDKPrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=True)
        self.prerequisite = JDKPrerequisite()


class TestBrewPrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=False)
        self.prerequisite = HomebrewPrerequisite()

    @mock.patch("shutil.which")
    def test_darwin_checker(self, shutil_which):
        shutil_which.return_value = None
        self.assertFalse(self.prerequisite.darwin_checker())
        shutil_which.return_value = "/opt/homebrew/bin/brew"
        self.assertTrue(self.prerequisite.darwin_checker())

    @mock.patch("pythonforandroid.prerequisites.info")
    def test_darwin_helper(self, info):
        self.prerequisite.darwin_helper()
        info.assert_called_once_with(
            "Installer for homebrew is not yet supported on macOS,"
            "the nice news is that the installation process is easy!"
            "See: https://brew.sh for further instructions."
        )


class TestOpenSSLPrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=True)
        self.prerequisite = OpenSSLPrerequisite()
        self.expected_homebrew_formula_name = "openssl@1.1"
        self.expected_homebrew_location_prefix = "/opt/homebrew/opt/openssl@1.1"

    @mock.patch(
        "pythonforandroid.prerequisites.Prerequisite._darwin_get_brew_formula_location_prefix"
    )
    def test_darwin_checker(self, _darwin_get_brew_formula_location_prefix):
        _darwin_get_brew_formula_location_prefix.return_value = None
        self.assertFalse(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.return_value = (
            self.expected_homebrew_location_prefix
        )
        self.assertTrue(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.assert_called_with(
            self.expected_homebrew_formula_name, installed=True
        )

    @mock.patch("pythonforandroid.prerequisites.subprocess.check_output")
    def test_darwin_installer(self, check_output):
        self.prerequisite.darwin_installer()
        check_output.assert_called_once_with(
            ["brew", "install", self.expected_homebrew_formula_name]
        )

    @mock.patch(
        "pythonforandroid.prerequisites.Prerequisite._darwin_get_brew_formula_location_prefix"
    )
    def test_darwin_pkg_config_location(self, _darwin_get_brew_formula_location_prefix):
        _darwin_get_brew_formula_location_prefix.return_value = (
            self.expected_homebrew_location_prefix
        )
        self.assertEqual(
            self.prerequisite.darwin_pkg_config_location(),
            f"{self.expected_homebrew_location_prefix}/lib/pkgconfig",
        )


class TestAutoconfPrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=True)
        self.prerequisite = AutoconfPrerequisite()

    @mock.patch(
        "pythonforandroid.prerequisites.Prerequisite._darwin_get_brew_formula_location_prefix"
    )
    def test_darwin_checker(self, _darwin_get_brew_formula_location_prefix):
        _darwin_get_brew_formula_location_prefix.return_value = None
        self.assertFalse(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.return_value = (
            "/opt/homebrew/opt/autoconf"
        )
        self.assertTrue(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.assert_called_with(
            "autoconf", installed=True
        )

    @mock.patch("pythonforandroid.prerequisites.subprocess.check_output")
    def test_darwin_installer(self, check_output):
        self.prerequisite.darwin_installer()
        check_output.assert_called_once_with(["brew", "install", "autoconf"])


class TestAutomakePrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=True)
        self.prerequisite = AutomakePrerequisite()

    @mock.patch(
        "pythonforandroid.prerequisites.Prerequisite._darwin_get_brew_formula_location_prefix"
    )
    def test_darwin_checker(self, _darwin_get_brew_formula_location_prefix):
        _darwin_get_brew_formula_location_prefix.return_value = None
        self.assertFalse(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.return_value = (
            "/opt/homebrew/opt/automake"
        )
        self.assertTrue(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.assert_called_with(
            "automake", installed=True
        )

    @mock.patch("pythonforandroid.prerequisites.subprocess.check_output")
    def test_darwin_installer(self, check_output):
        self.prerequisite.darwin_installer()
        check_output.assert_called_once_with(["brew", "install", "automake"])


class TestLibtoolPrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=True)
        self.prerequisite = LibtoolPrerequisite()

    @mock.patch(
        "pythonforandroid.prerequisites.Prerequisite._darwin_get_brew_formula_location_prefix"
    )
    def test_darwin_checker(self, _darwin_get_brew_formula_location_prefix):
        _darwin_get_brew_formula_location_prefix.return_value = None
        self.assertFalse(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.return_value = (
            "/opt/homebrew/opt/libtool"
        )
        self.assertTrue(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.assert_called_with(
            "libtool", installed=True
        )

    @mock.patch("pythonforandroid.prerequisites.subprocess.check_output")
    def test_darwin_installer(self, check_output):
        self.prerequisite.darwin_installer()
        check_output.assert_called_once_with(["brew", "install", "libtool"])


class TestPkgConfigPrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=True)
        self.prerequisite = PkgConfigPrerequisite()

    @mock.patch(
        "pythonforandroid.prerequisites.Prerequisite._darwin_get_brew_formula_location_prefix"
    )
    def test_darwin_checker(self, _darwin_get_brew_formula_location_prefix):
        _darwin_get_brew_formula_location_prefix.return_value = None
        self.assertFalse(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.return_value = (
            "/opt/homebrew/opt/pkg-config"
        )
        self.assertTrue(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.assert_called_with(
            "pkg-config", installed=True
        )

    @mock.patch("pythonforandroid.prerequisites.subprocess.check_output")
    def test_darwin_installer(self, check_output):
        self.prerequisite.darwin_installer()
        check_output.assert_called_once_with(["brew", "install", "pkg-config"])


class TestCmakePrerequisite(PrerequisiteSetUpBaseClass, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.mandatory = dict(linux=False, darwin=True)
        self.installer_is_supported = dict(linux=False, darwin=True)
        self.prerequisite = CmakePrerequisite()

    @mock.patch(
        "pythonforandroid.prerequisites.Prerequisite._darwin_get_brew_formula_location_prefix"
    )
    def test_darwin_checker(self, _darwin_get_brew_formula_location_prefix):
        _darwin_get_brew_formula_location_prefix.return_value = None
        self.assertFalse(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.return_value = (
            "/opt/homebrew/opt/cmake"
        )
        self.assertTrue(self.prerequisite.darwin_checker())
        _darwin_get_brew_formula_location_prefix.assert_called_with(
            "cmake", installed=True
        )

    @mock.patch("pythonforandroid.prerequisites.subprocess.check_output")
    def test_darwin_installer(self, check_output):
        self.prerequisite.darwin_installer()
        check_output.assert_called_once_with(["brew", "install", "cmake"])


class TestDefaultPrerequisitesCheckandInstall(unittest.TestCase):

    def test_default_darwin_prerequisites_set(self):
        self.assertListEqual(
            [
                p.__class__.__name__
                for p in get_required_prerequisites(platform="darwin")
            ],
            [
                "HomebrewPrerequisite",
                "AutoconfPrerequisite",
                "AutomakePrerequisite",
                "LibtoolPrerequisite",
                "PkgConfigPrerequisite",
                "CmakePrerequisite",
                "OpenSSLPrerequisite",
                "JDKPrerequisite",
            ],
        )

    def test_default_linux_prerequisites_set(self):
        self.assertListEqual(
            [
                p.__class__.__name__
                for p in get_required_prerequisites(platform="linux")
            ],
            [
            ],
        )
