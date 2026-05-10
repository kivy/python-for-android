from unittest import mock

from pythonforandroid.entrypoints import main
from pythonforandroid.util import BuildInterruptingException


class TestMain:
    """Test the main entry point function."""

    @mock.patch('pythonforandroid.toolchain.ToolchainCL')
    @mock.patch('pythonforandroid.entrypoints.check_python_version')
    def test_main_success(self, mock_check_version, mock_toolchain):
        """Test main() executes successfully with valid Python version."""
        main()

        mock_check_version.assert_called_once()
        mock_toolchain.assert_called_once()

    @mock.patch('pythonforandroid.entrypoints.handle_build_exception')
    @mock.patch('pythonforandroid.toolchain.ToolchainCL')
    @mock.patch('pythonforandroid.entrypoints.check_python_version')
    def test_main_build_interrupting_exception(
        self, mock_check_version, mock_toolchain, mock_handler
    ):
        """Test main() catches BuildInterruptingException and handles it."""
        exc = BuildInterruptingException("Build failed", "Try reinstalling")
        mock_toolchain.side_effect = exc

        main()

        mock_check_version.assert_called_once()
        mock_toolchain.assert_called_once()
        mock_handler.assert_called_once_with(exc)

    @mock.patch('pythonforandroid.toolchain.ToolchainCL')
    @mock.patch('pythonforandroid.entrypoints.check_python_version')
    def test_main_other_exception_propagates(
        self, mock_check_version, mock_toolchain
    ):
        """Test main() allows non-BuildInterruptingException to propagate."""
        mock_toolchain.side_effect = RuntimeError("Unexpected error")

        try:
            main()
            assert False, "Expected RuntimeError to be raised"
        except RuntimeError as e:
            assert str(e) == "Unexpected error"

        mock_check_version.assert_called_once()
        mock_toolchain.assert_called_once()

    @mock.patch('pythonforandroid.entrypoints.check_python_version')
    def test_main_python_version_check_fails(self, mock_check_version):
        """Test main() allows Python version check failure to propagate."""
        mock_check_version.side_effect = SystemExit(1)

        try:
            main()
            assert False, "Expected SystemExit to be raised"
        except SystemExit as e:
            assert e.code == 1

        mock_check_version.assert_called_once()
