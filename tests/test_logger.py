import unittest
from unittest.mock import MagicMock
from pythonforandroid import logger


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
