import logging
import sh
import pytest
import unittest
from unittest.mock import MagicMock, Mock, patch
from pythonforandroid import logger


class TestColorSetup:
    """Test color setup and configuration."""

    def teardown_method(self):
        """Reset color state after each test to avoid affecting other tests."""
        logger.setup_color('never')

    def test_setup_color_never(self):
        """Test color disabled when set to 'never'."""
        logger.setup_color('never')
        assert not logger.Out_Style._enabled
        assert not logger.Out_Fore._enabled
        assert not logger.Err_Style._enabled
        assert not logger.Err_Fore._enabled

    def test_setup_color_always(self):
        """Test color enabled when set to 'always'."""
        logger.setup_color('always')
        assert logger.Out_Style._enabled
        assert logger.Out_Fore._enabled
        assert logger.Err_Style._enabled
        assert logger.Err_Fore._enabled

    @patch('pythonforandroid.logger.stdout')
    @patch('pythonforandroid.logger.stderr')
    def test_setup_color_auto_with_tty(self, mock_stderr, mock_stdout):
        """Test color enabled when auto and isatty() returns True."""
        mock_stdout.isatty.return_value = True
        mock_stderr.isatty.return_value = True
        logger.setup_color('auto')
        assert logger.Out_Style._enabled
        assert logger.Err_Style._enabled


class TestUtilityFunctions:
    """Test logger utility functions."""

    def test_shorten_string_short(self):
        """Test shorten_string returns string unchanged when under limit."""
        result = logger.shorten_string("short", 50)
        assert result == "short"

    def test_shorten_string_long(self):
        """Test shorten_string truncates long strings correctly."""
        long_string = "a" * 100
        result = logger.shorten_string(long_string, 50)
        assert "...(and" in result
        assert "more)" in result
        assert len(result) <= 50

    def test_shorten_string_bytes(self):
        """Test shorten_string handles bytes input."""
        byte_string = b"test" * 50
        result = logger.shorten_string(byte_string, 50)
        assert "...(and" in result

    @patch.dict('os.environ', {'COLUMNS': '120'})
    def test_get_console_width_from_env(self):
        """Test get_console_width reads from COLUMNS env var."""
        width = logger.get_console_width()
        assert width == 120

    @patch.dict('os.environ', {}, clear=True)
    @patch('os.popen')
    def test_get_console_width_from_stty(self, mock_popen):
        """Test get_console_width falls back to stty command."""
        mock_popen.return_value.read.return_value = "40 80"
        width = logger.get_console_width()
        assert width == 80
        mock_popen.assert_called_once_with('stty size', 'r')

    @patch.dict('os.environ', {}, clear=True)
    @patch('os.popen')
    def test_get_console_width_default(self, mock_popen):
        """Test get_console_width returns default when stty fails."""
        mock_popen.return_value.read.side_effect = Exception("stty failed")
        width = logger.get_console_width()
        assert width == 100


class TestLevelDifferentiatingFormatter:
    """Test custom log message formatter."""

    def test_format_error_level(self):
        """Test formatter adds [ERROR] prefix for ERROR level."""
        formatter = logger.LevelDifferentiatingFormatter('%(message)s')
        record = logging.LogRecord(
            name='test', level=40, pathname='', lineno=0,
            msg='test error', args=(), exc_info=None
        )
        formatted = formatter.format(record)
        assert '[ERROR]' in formatted

    def test_format_warning_level(self):
        """Test formatter adds [WARNING] prefix for WARNING level."""
        formatter = logger.LevelDifferentiatingFormatter('%(message)s')
        record = logging.LogRecord(
            name='test', level=30, pathname='', lineno=0,
            msg='test warning', args=(), exc_info=None
        )
        formatted = formatter.format(record)
        assert '[WARNING]' in formatted

    def test_format_info_level(self):
        """Test formatter adds [INFO] prefix for INFO level."""
        formatter = logger.LevelDifferentiatingFormatter('%(message)s')
        record = logging.LogRecord(
            name='test', level=20, pathname='', lineno=0,
            msg='test info', args=(), exc_info=None
        )
        formatted = formatter.format(record)
        assert '[INFO]' in formatted

    def test_format_debug_level(self):
        """Test formatter adds [DEBUG] prefix for DEBUG level."""
        formatter = logger.LevelDifferentiatingFormatter('%(message)s')
        record = logging.LogRecord(
            name='test', level=10, pathname='', lineno=0,
            msg='test debug', args=(), exc_info=None
        )
        formatted = formatter.format(record)
        assert '[DEBUG]' in formatted


class TestShprintErrorHandling:
    """Test shprint error handling and edge cases."""

    @patch('pythonforandroid.logger.get_console_width')
    def test_shprint_with_filter(self, mock_width):
        """Test shprint filters output with _filter parameter."""
        mock_width.return_value = 100

        command = MagicMock()
        # Create a mock error with required attributes
        error = Mock(spec=sh.ErrorReturnCode)
        error.stdout = b'line1\nfiltered_line\nline3'
        error.stderr = b''
        command.side_effect = error

        with pytest.raises(TypeError):
            logger.shprint(command, _filter='filtered', _tail=10)

    @patch('pythonforandroid.logger.get_console_width')
    def test_shprint_with_filterout(self, mock_width):
        """Test shprint excludes output with _filterout parameter."""
        mock_width.return_value = 100

        command = MagicMock()
        error = Mock(spec=sh.ErrorReturnCode)
        error.stdout = b'keep1\nexclude_line\nkeep2'
        error.stderr = b''
        command.side_effect = error

        with pytest.raises(TypeError):
            logger.shprint(command, _filterout='exclude', _tail=10)

    @patch('pythonforandroid.logger.get_console_width')
    @patch('pythonforandroid.logger.stdout')
    @patch.dict('os.environ', {'P4A_FULL_DEBUG': '1'})
    def test_shprint_full_debug_mode(self, mock_stdout, mock_width):
        """Test shprint in P4A_FULL_DEBUG mode shows all output."""
        mock_width.return_value = 100

        command = MagicMock()
        command.return_value = iter(['debug line 1\n', 'debug line 2\n'])

        logger.shprint(command)
        # In full debug mode, output is written directly to stdout
        assert mock_stdout.write.called

    @patch('pythonforandroid.logger.get_console_width')
    @patch.dict('os.environ', {}, clear=True)
    def test_shprint_critical_failure_exits(self, mock_width):
        """Test shprint exits on critical command failure."""
        mock_width.return_value = 100

        command = MagicMock()

        # Create a proper exception class that mimics sh.ErrorReturnCode
        class MockErrorReturnCode(sh.ErrorReturnCode):
            def __init__(self):
                self.full_cmd = 'test'
                self.stdout = b'output'
                self.stderr = b'error'
                self.exit_code = 1

        error = MockErrorReturnCode()
        command.side_effect = error

        with patch('pythonforandroid.logger.exit', side_effect=SystemExit) as mock_exit:
            with pytest.raises(SystemExit):
                logger.shprint(command, _critical=True, _tail=5)
            mock_exit.assert_called_once_with(1)


class TestLoggingHelpers:
    """Test logging helper functions."""

    @patch('pythonforandroid.logger.logger')
    def test_info_main(self, mock_logger):
        """Test info_main logs with bright green formatting."""
        logger.info_main('test', 'message')
        mock_logger.info.assert_called_once()
        # Verify the call contains color codes and text
        call_args = mock_logger.info.call_args[0][0]
        assert 'test' in call_args
        assert 'message' in call_args

    @patch('pythonforandroid.logger.info')
    def test_info_notify(self, mock_info):
        """Test info_notify logs with blue formatting."""
        logger.info_notify('notification')
        mock_info.assert_called_once()
        call_args = mock_info.call_args[0][0]
        assert 'notification' in call_args


class TestShprint(unittest.TestCase):

    def test_unicode_encode(self):
        """
        Makes sure `shprint()` can handle unicode command output.
        Running the test with PYTHONIOENCODING=ASCII env would fail, refs:
        https://github.com/kivy/python-for-android/issues/1654
        """
        expected_command_output = ["foo\xa0bar"]
        command = MagicMock()
        command.return_value = expected_command_output
        output = logger.shprint(command, 'a1', k1='k1')
        self.assertEqual(output, expected_command_output)
