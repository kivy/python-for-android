
# This test is a special case that we expect to run under Python 2, so
# include the necessary compatibility imports:
try:  # Python 3
    from unittest import mock
except ImportError:  # Python 2
    import mock

from pythonforandroid.recommendations import PY2_ERROR_TEXT
from pythonforandroid import entrypoints


def test_main_python2():
    """Test that running under Python 2 leads to the build failing, while
    running under a suitable version works fine.

    Note that this test must be run *using* Python 2 to truly test
    that p4a can reach the Python version check before importing some
    Python-3-only syntax and crashing.
    """

    # Under Python 2, we should get a normal control flow exception
    # that is handled properly, not any other type of crash
    handle_exception_path = 'pythonforandroid.entrypoints.handle_build_exception'
    with mock.patch('sys.version_info') as fake_version_info, \
         mock.patch(handle_exception_path) as handle_build_exception:  # noqa: E127

        fake_version_info.major = 2
        fake_version_info.minor = 7

        def check_python2_exception(exc):
            """Check that the exception message is Python 2 specific."""
            assert exc.message == PY2_ERROR_TEXT
        handle_build_exception.side_effect = check_python2_exception

        entrypoints.main()

    handle_build_exception.assert_called_once()
