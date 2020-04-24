import os
import types
import unittest
from unittest import mock

from pythonforandroid import util


class TestUtil(unittest.TestCase):
    """
    An inherited class of `unittest.TestCase`to test the module
    :mod:`~pythonforandroid.util`.
    """

    @mock.patch("pythonforandroid.util.makedirs")
    def test_ensure_dir(self, mock_makedirs):
        """
        Basic test for method :meth:`~pythonforandroid.util.ensure_dir`. Here
        we make sure that the mentioned method is called only once.
        """
        util.ensure_dir("fake_directory")
        mock_makedirs.assert_called_once_with("fake_directory")

    @mock.patch("shutil.rmtree")
    @mock.patch("pythonforandroid.util.mkdtemp")
    def test_temp_directory(self, mock_mkdtemp, mock_shutil_rmtree):
        """
        Basic test for method :meth:`~pythonforandroid.util.temp_directory`. We
        perform this test by `mocking` the command `mkdtemp` and
        `shutil.rmtree` and we make sure that those functions are called in the
        proper place.
        """
        mock_mkdtemp.return_value = "/temp/any_directory"
        with util.temp_directory():
            mock_mkdtemp.assert_called_once()
            mock_shutil_rmtree.assert_not_called()
        mock_shutil_rmtree.assert_called_once_with("/temp/any_directory")

    @mock.patch("pythonforandroid.util.chdir")
    def test_current_directory(self, moch_chdir):
        """
        Basic test for method :meth:`~pythonforandroid.util.current_directory`.
        We `mock` chdir and we check that the command is executed once we are
        inside a python's `with` statement. Then we check that `chdir has been
        called with the proper arguments inside this `with` statement and also
        that, once we leave the `with` statement, is called again with the
        current working path.
        """
        chdir_dir = "/temp/any_directory"
        # test chdir to existing directory
        with util.current_directory(chdir_dir):
            moch_chdir.assert_called_once_with("/temp/any_directory")
        moch_chdir.assert_has_calls(
            [mock.call("/temp/any_directory"), mock.call(os.getcwd())]
        )

    def test_current_directory_exception(self):
        """
        Another test for method
        :meth:`~pythonforandroid.util.current_directory`, but here we check
        that using the method with a non-existing-directory raises an `OSError`
        exception.

        .. note:: test chdir to non-existing directory, should raise error,
            for py3 the exception is FileNotFoundError and IOError for py2, to
            avoid introduce conditions, we test with a more generic exception
        """
        with self.assertRaises(OSError), util.current_directory(
            "/fake/directory"
        ):
            pass

    @mock.patch("pythonforandroid.util.walk")
    def test_walk_valid_filens(self, mock_walk):
        """
        Test method :meth:`~pythonforandroid.util.walk_valid_filens`
        In here we simulate the following directory structure:

        /fake_dir
         |-- README
         |-- setup.py
         |-- __pycache__
         |--     |__
         |__Lib
             |-- abc.pyc
             |-- abc.py
             |__ ctypes
                  |-- util.pyc
                  |-- util.py

        Then we execute the method in order to check that we got the expected
        result, which should be:

        .. code-block:: python
           :emphasize-lines: 2-4

        expected_result = {
            "/fake_dir/README",
            "/fake_dir/Lib/abc.pyc",
            "/fake_dir/Lib/ctypes/util.pyc",
        }
        """
        simulated_walk_result = [
            ["/fake_dir", ["__pycache__", "Lib"], ["README", "setup.py"]],
            ["/fake_dir/Lib", ["ctypes"], ["abc.pyc", "abc.py"]],
            ["/fake_dir/Lib/ctypes", [], ["util.pyc", "util.py"]],
        ]
        mock_walk.return_value = simulated_walk_result
        file_ens = util.walk_valid_filens(
            "/fake_dir", ["__pycache__"], ["*.py"]
        )
        self.assertIsInstance(file_ens, types.GeneratorType)
        expected_result = {
            "/fake_dir/README",
            "/fake_dir/Lib/abc.pyc",
            "/fake_dir/Lib/ctypes/util.pyc",
        }
        result = set(file_ens)

        self.assertEqual(result, expected_result)

    def test_util_exceptions(self):
        """
        Test exceptions for a couple of methods:

           - method :meth:`~pythonforandroid.util.BuildInterruptingException`
           - method :meth:`~pythonforandroid.util.handle_build_exception`

        Here we create an exception with method
        :meth:`~pythonforandroid.util.BuildInterruptingException` and we run it
        inside method :meth:`~pythonforandroid.util.handle_build_exception` to
        make sure that it raises an `SystemExit`.
        """
        exc = util.BuildInterruptingException(
            "missing dependency xxx", instructions="pip install --user xxx"
        )
        with self.assertRaises(SystemExit):
            util.handle_build_exception(exc)
