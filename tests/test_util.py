import os
import types
import unittest

try:
    from unittest import mock
except ImportError:
    # `Python 2` or lower than `Python 3.3` does not
    # have the `unittest.mock` module built-in
    import mock
from pythonforandroid import util


class TestUtil(unittest.TestCase):
    @mock.patch("pythonforandroid.util.makedirs")
    def test_ensure_dir(self, mock_makedirs):
        util.ensure_dir("fake_directory")
        mock_makedirs.assert_called_once_with("fake_directory")

    @mock.patch("shutil.rmtree")
    @mock.patch("pythonforandroid.util.mkdtemp")
    def test_temp_directory(self, mock_mkdtemp, mock_shutil_rmtree):
        mock_mkdtemp.return_value = "/temp/any_directory"
        with util.temp_directory():
            mock_mkdtemp.assert_called_once()
        mock_shutil_rmtree.assert_called_once_with("/temp/any_directory")

    @mock.patch("pythonforandroid.util.chdir")
    def test_current_directory(self, moch_chdir):
        chdir_dir = "/temp/any_directory"
        # test chdir to existing directory
        with util.current_directory(chdir_dir):
            moch_chdir.assert_called_once_with("/temp/any_directory")
        moch_chdir.assert_has_calls(
            [
                mock.call("/temp/any_directory"),
                mock.call(os.getcwd()),
            ]
        )

    def test_current_directory_exception(self):
        # test chdir to non-existing directory, should raise error
        # for py3 the exception is FileNotFoundError and IOError for py2, to
        # avoid introduce conditions, we test with a more generic exception
        with self.assertRaises(OSError):
            with util.current_directory("/fake/directory"):
                # the line below will never be executed
                print("")

    @mock.patch("pythonforandroid.util.sh.which")
    def test_get_virtualenv_executable(self, mock_sh_which):
        # test that all calls to `sh.which` are performed, so we expect the
        # first two `sh.which` calls should be None and the last one should
        # return the expected virtualenv (the python3 one)
        expected_venv = os.path.join(
            os.path.expanduser("~"), ".local/bin/virtualenv"
        )
        mock_sh_which.side_effect = [None, None, expected_venv]
        self.assertEqual(util.get_virtualenv_executable(), expected_venv)
        mock_sh_which.assert_has_calls(
            [
                mock.call("virtualenv2"),
                mock.call("virtualenv-2.7"),
                mock.call("virtualenv"),
            ]
        )
        self.assertEqual(mock_sh_which.call_count, 3)
        mock_sh_which.reset_mock()

        # Now test that we don't have virtualenv installed, so all calls to
        # `sh.which` should return None
        mock_sh_which.side_effect = [None, None, None]
        self.assertIsNone(util.get_virtualenv_executable())
        self.assertEqual(mock_sh_which.call_count, 3)
        mock_sh_which.assert_has_calls(
            [
                mock.call("virtualenv2"),
                mock.call("virtualenv-2.7"),
                mock.call("virtualenv"),
            ]
        )

    def test_walk_valid_filens_sample(self):
        file_ens = util.walk_valid_filens(
            "/home/opacam/Devel/python-for-android/tests/",
            ["__pycache__"],
            ["*.pyc"],
        )
        for i in os.walk("/home/opacam/Devel/python-for-android/tests/"):
            print(i)
        for i in file_ens:
            print(i)

    @mock.patch("pythonforandroid.util.walk")
    def test_walk_valid_filens(self, mock_walk):
        simulated_walk_result = [
            ["/fake_dir", ["__pycache__", "Lib"], ["README", "setup.py"]],
            ["/fake_dir/Lib", ["ctypes"], ["abc.pyc", "abc.py"]],
            ["/fake_dir/Lib/ctypes", [], ["util.pyc", "util.py"]],
        ]
        # /fake_dir
        #  |-- README
        #  |-- setup.py
        #  |-- __pycache__
        #  |--     |__
        #  |__Lib
        #      |-- abc.pyc
        #      |-- abc.py
        #      |__ ctypes
        #           |-- util.pyc
        #           |-- util.py
        mock_walk.return_value = simulated_walk_result
        file_ens = util.walk_valid_filens(
            "/fake_dir", ["__pycache__"], ["*.py"]
        )
        self.assertIsInstance(file_ens, types.GeneratorType)
        # given the simulated structure we expect:
        expected_result = {
            "/fake_dir/README",
            "/fake_dir/Lib/abc.pyc",
            "/fake_dir/Lib/ctypes/util.pyc",
        }
        result = set()
        for i in file_ens:
            result.add(i)

        self.assertEqual(result, expected_result)

    def test_util_exceptions(self):
        exc = util.BuildInterruptingException(
            "missing dependency xxx", instructions="pip install --user xxx"
        )
        with self.assertRaises(SystemExit):
            util.handle_build_exception(exc)
