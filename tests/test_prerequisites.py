import unittest
from unittest import mock, skipIf

import sys
import pytest

from pythonforandroid.prerequisites import (
    Prerequisite,
    JDKPrerequisite,
    HomebrewPrerequisite,
    OpenSSLPrerequisite,
    AutoconfPrerequisite,
    AutomakePrerequisite,
    LibtoolPrerequisite,
    PkgConfigPrerequisite,
    CmakePrerequisite,
    get_required_prerequisites,
    check_and_install_default_prerequisites,
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
        self.expected_homebrew_formula_name = "openssl@3"
        self.expected_homebrew_location_prefix = "/opt/homebrew/opt/openssl@3"

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


class TestPrerequisiteBaseClass:
    """Test base Prerequisite class methods."""

    @mock.patch('pythonforandroid.prerequisites.info')
    @mock.patch.object(Prerequisite, 'checker')
    def test_is_valid_when_met(self, mock_checker, mock_info):
        """Test is_valid returns True when prerequisite is met."""
        mock_checker.return_value = True
        prerequisite = Prerequisite()
        result = prerequisite.is_valid()
        assert result == (True, "")
        mock_info.assert_called()
        assert "is met" in mock_info.call_args[0][0]

    @mock.patch('pythonforandroid.prerequisites.warning')
    @mock.patch.object(Prerequisite, 'checker')
    def test_is_valid_when_not_met_non_mandatory(self, mock_checker, mock_warning):
        """Test is_valid warns when non-mandatory prerequisite not met."""
        mock_checker.return_value = False
        prerequisite = Prerequisite()
        prerequisite.mandatory = dict(linux=False, darwin=False)

        result = prerequisite.is_valid()
        assert result is None
        mock_warning.assert_called()
        assert "not met" in mock_warning.call_args[0][0]

    @mock.patch('pythonforandroid.prerequisites.error')
    @mock.patch.object(Prerequisite, 'checker')
    @mock.patch('sys.platform', 'linux')
    def test_is_valid_when_not_met_mandatory(self, mock_checker, mock_error):
        """Test is_valid errors when mandatory prerequisite not met."""
        mock_checker.return_value = False
        prerequisite = Prerequisite()
        prerequisite.mandatory = dict(linux=True, darwin=False)

        result = prerequisite.is_valid()
        assert result is None
        mock_error.assert_called()
        assert "not met" in mock_error.call_args[0][0]

    @mock.patch('sys.platform', 'linux')
    @mock.patch.object(Prerequisite, 'linux_checker')
    def test_checker_calls_linux_checker(self, mock_linux_checker):
        """Test checker dispatches to linux_checker on Linux."""
        mock_linux_checker.return_value = True
        prerequisite = Prerequisite()
        result = prerequisite.checker()
        assert result is True
        mock_linux_checker.assert_called_once()

    @mock.patch('sys.platform', 'darwin')
    @mock.patch.object(Prerequisite, 'darwin_checker')
    def test_checker_calls_darwin_checker(self, mock_darwin_checker):
        """Test checker dispatches to darwin_checker on macOS."""
        mock_darwin_checker.return_value = True
        prerequisite = Prerequisite()
        result = prerequisite.checker()
        assert result is True
        mock_darwin_checker.assert_called_once()

    @mock.patch('sys.platform', 'win32')
    def test_checker_raises_on_unsupported_platform(self):
        """Test checker raises exception on unsupported platform."""
        prerequisite = Prerequisite()
        with pytest.raises(Exception, match="Unsupported platform"):
            prerequisite.checker()


class TestPrerequisiteInstallation:
    """Test prerequisite installation workflow."""

    @mock.patch.dict('os.environ', {'PYTHONFORANDROID_PREREQUISITES_INSTALL_INTERACTIVE': '1'})
    @mock.patch('builtins.input')
    def test_ask_to_install_user_accepts(self, mock_input):
        """Test ask_to_install returns True when user enters 'y'."""
        prerequisite = Prerequisite()
        prerequisite.name = "TestPrerequisite"
        mock_input.return_value = 'y'
        result = prerequisite.ask_to_install()
        assert result is True

    @mock.patch.dict('os.environ', {'PYTHONFORANDROID_PREREQUISITES_INSTALL_INTERACTIVE': '1'})
    @mock.patch('builtins.input')
    def test_ask_to_install_user_declines(self, mock_input):
        """Test ask_to_install returns False when user enters 'n'."""
        prerequisite = Prerequisite()
        prerequisite.name = "TestPrerequisite"
        mock_input.return_value = 'n'
        result = prerequisite.ask_to_install()
        assert result is False

    @mock.patch.dict('os.environ', {'PYTHONFORANDROID_PREREQUISITES_INSTALL_INTERACTIVE': '0'})
    @mock.patch('pythonforandroid.prerequisites.info')
    def test_ask_to_install_non_interactive(self, mock_info):
        """Test ask_to_install returns True in non-interactive mode (CI)."""
        prerequisite = Prerequisite()
        prerequisite.name = "TestPrerequisite"
        result = prerequisite.ask_to_install()
        assert result is True
        mock_info.assert_called()
        assert "not interactive" in mock_info.call_args[0][0]

    @mock.patch('sys.platform', 'linux')
    @mock.patch.object(Prerequisite, 'ask_to_install')
    @mock.patch.object(Prerequisite, 'linux_installer')
    @mock.patch('pythonforandroid.prerequisites.info')
    def test_install_when_user_accepts_linux(self, mock_info, mock_installer, mock_ask):
        """Test install calls linux_installer when user accepts on Linux."""
        prerequisite = Prerequisite()
        prerequisite.installer_is_supported = dict(linux=True, darwin=True)
        mock_ask.return_value = True
        prerequisite.install()
        mock_installer.assert_called_once()

    @mock.patch('sys.platform', 'darwin')
    @mock.patch.object(Prerequisite, 'ask_to_install')
    @mock.patch.object(Prerequisite, 'darwin_installer')
    def test_install_when_user_accepts_darwin(self, mock_installer, mock_ask):
        """Test install calls darwin_installer when user accepts on macOS."""
        prerequisite = Prerequisite()
        prerequisite.installer_is_supported = dict(linux=True, darwin=True)
        mock_ask.return_value = True
        prerequisite.install()
        mock_installer.assert_called_once()

    @mock.patch.object(Prerequisite, 'ask_to_install')
    @mock.patch('pythonforandroid.prerequisites.info')
    def test_install_when_user_declines(self, mock_info, mock_ask):
        """Test install skips installation when user declines."""
        prerequisite = Prerequisite()
        prerequisite.name = "TestPrerequisite"
        mock_ask.return_value = False
        prerequisite.install()
        mock_info.assert_called()
        assert "Skipping" in mock_info.call_args[0][0]

    def test_install_is_supported(self):
        """Test install_is_supported returns correct platform support."""
        prerequisite = Prerequisite()
        prerequisite.installer_is_supported = dict(linux=True, darwin=False)
        with mock.patch('sys.platform', 'linux'):
            assert prerequisite.install_is_supported() is True


class TestJDKPrerequisiteVersionChecking:
    """Test JDK version checking logic."""

    @mock.patch('pythonforandroid.prerequisites.subprocess.Popen')
    @mock.patch('os.path.exists')
    def test_darwin_jdk_is_supported_valid_version(self, mock_exists, mock_popen):
        """Test _darwin_jdk_is_supported returns True for valid JDK 17."""
        prerequisite = JDKPrerequisite()
        mock_exists.return_value = True

        # Mock javac version output
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'javac 17.0.2\n', b'')
        mock_popen.return_value = mock_process

        result = prerequisite._darwin_jdk_is_supported('/path/to/jdk')
        assert result is True

    @mock.patch('pythonforandroid.prerequisites.subprocess.Popen')
    @mock.patch('os.path.exists')
    def test_darwin_jdk_is_supported_invalid_version(self, mock_exists, mock_popen):
        """Test _darwin_jdk_is_supported returns False for wrong JDK version."""
        prerequisite = JDKPrerequisite()
        mock_exists.return_value = True

        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'javac 11.0.1\n', b'')
        mock_popen.return_value = mock_process

        result = prerequisite._darwin_jdk_is_supported('/path/to/jdk')
        assert result is False

    @mock.patch('os.path.exists')
    def test_darwin_jdk_is_supported_no_javac(self, mock_exists):
        """Test _darwin_jdk_is_supported returns False when javac doesn't exist."""
        prerequisite = JDKPrerequisite()
        mock_exists.return_value = False
        result = prerequisite._darwin_jdk_is_supported('/path/to/jdk')
        assert result is False

    @mock.patch('pythonforandroid.prerequisites.subprocess.run')
    def test_darwin_get_libexec_jdk_path(self, mock_run):
        """Test _darwin_get_libexec_jdk_path calls java_home correctly."""
        prerequisite = JDKPrerequisite()
        mock_run.return_value = mock.Mock(stdout=b'/Library/Java/JDK/17\n')

        result = prerequisite._darwin_get_libexec_jdk_path(version='17')
        assert result == '/Library/Java/JDK/17'
        mock_run.assert_called_once()
        assert '-v' in mock_run.call_args[0][0]
        assert '17' in mock_run.call_args[0][0]

    @mock.patch.dict('os.environ', {'JAVA_HOME': '/custom/jdk'})
    @mock.patch.object(JDKPrerequisite, '_darwin_jdk_is_supported')
    def test_darwin_checker_uses_java_home_env(self, mock_is_supported):
        """Test darwin_checker uses JAVA_HOME env var if set."""
        prerequisite = JDKPrerequisite()
        mock_is_supported.return_value = True

        result = prerequisite.darwin_checker()
        assert result is True
        mock_is_supported.assert_called_with('/custom/jdk')


class TestHomebrewHelpers:
    """Test Homebrew helper methods."""

    @mock.patch('pythonforandroid.prerequisites.subprocess.Popen')
    def test_darwin_get_brew_formula_location_prefix_success(self, mock_popen):
        """Test _darwin_get_brew_formula_location_prefix returns path on success."""
        prerequisite = Prerequisite()
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'/opt/homebrew/opt/openssl@3\n', b'')
        mock_popen.return_value = mock_process

        result = prerequisite._darwin_get_brew_formula_location_prefix('openssl@3')
        assert result == '/opt/homebrew/opt/openssl@3'
        mock_popen.assert_called_once()
        assert 'brew' in mock_popen.call_args[0][0]
        assert '--prefix' in mock_popen.call_args[0][0]

    @mock.patch('pythonforandroid.prerequisites.subprocess.Popen')
    @mock.patch('pythonforandroid.prerequisites.error')
    def test_darwin_get_brew_formula_location_prefix_failure(self, mock_error, mock_popen):
        """Test _darwin_get_brew_formula_location_prefix returns None on failure."""
        prerequisite = Prerequisite()
        mock_process = mock.Mock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b'', b'Formula not found\n')
        mock_popen.return_value = mock_process

        result = prerequisite._darwin_get_brew_formula_location_prefix('nonexistent')
        assert result is None
        mock_error.assert_called()

    @mock.patch('pythonforandroid.prerequisites.subprocess.Popen')
    def test_darwin_get_brew_formula_location_prefix_with_installed_flag(self, mock_popen):
        """Test _darwin_get_brew_formula_location_prefix uses --installed flag."""
        prerequisite = Prerequisite()
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'/opt/homebrew/opt/cmake\n', b'')
        mock_popen.return_value = mock_process

        prerequisite._darwin_get_brew_formula_location_prefix('cmake', installed=True)
        assert '--installed' in mock_popen.call_args[0][0]


class TestCheckAndInstallPrerequisites:
    """Test main prerequisite checking workflow."""

    @mock.patch('pythonforandroid.prerequisites.get_required_prerequisites')
    def test_check_and_install_all_met(self, mock_get_prereqs):
        """Test check_and_install when all prerequisites are met."""
        # Create mock prerequisites that are all valid
        mock_prereq1 = mock.Mock()
        mock_prereq1.is_valid.return_value = True
        mock_prereq2 = mock.Mock()
        mock_prereq2.is_valid.return_value = True

        mock_get_prereqs.return_value = [mock_prereq1, mock_prereq2]

        check_and_install_default_prerequisites()

        # Verify prerequisites were checked
        mock_prereq1.is_valid.assert_called_once()
        mock_prereq2.is_valid.assert_called_once()

        # Verify no installation attempted
        mock_prereq1.install.assert_not_called()
        mock_prereq2.install.assert_not_called()

    @mock.patch('pythonforandroid.prerequisites.get_required_prerequisites')
    def test_check_and_install_some_not_met(self, mock_get_prereqs):
        """Test check_and_install when some prerequisites are not met."""
        # First prerequisite valid, second not valid but has installer
        mock_prereq1 = mock.Mock()
        mock_prereq1.is_valid.return_value = True

        mock_prereq2 = mock.Mock()
        mock_prereq2.is_valid.return_value = False
        mock_prereq2.install_is_supported.return_value = True

        mock_get_prereqs.return_value = [mock_prereq1, mock_prereq2]

        check_and_install_default_prerequisites()

        # Verify second prerequisite triggers installation workflow
        mock_prereq2.show_helper.assert_called_once()
        mock_prereq2.install.assert_called_once()
