import unittest
from os.path import join
from sys import version as py_version

import packaging.version
from unittest import mock
from pythonforandroid.recommendations import (
    check_ndk_api,
    check_ndk_version,
    check_target_api,
    read_ndk_version,
    check_python_version,
    print_recommendations,
    MAX_NDK_VERSION,
    RECOMMENDED_NDK_VERSION,
    RECOMMENDED_TARGET_API,
    MIN_NDK_API,
    MIN_NDK_VERSION,
    NDK_DOWNLOAD_URL,
    ARMEABI_MAX_TARGET_API,
    MIN_TARGET_API,
    UNKNOWN_NDK_MESSAGE,
    PARSE_ERROR_NDK_MESSAGE,
    READ_ERROR_NDK_MESSAGE,
    ENSURE_RIGHT_NDK_MESSAGE,
    NDK_LOWER_THAN_SUPPORTED_MESSAGE,
    UNSUPPORTED_NDK_API_FOR_ARMEABI_MESSAGE,
    CURRENT_NDK_VERSION_MESSAGE,
    RECOMMENDED_NDK_VERSION_MESSAGE,
    TARGET_NDK_API_GREATER_THAN_TARGET_API_MESSAGE,
    OLD_NDK_API_MESSAGE,
    NEW_NDK_MESSAGE,
    OLD_API_MESSAGE,
    MIN_PYTHON_MAJOR_VERSION,
    MIN_PYTHON_MINOR_VERSION,
    PY2_ERROR_TEXT,
    PY_VERSION_ERROR_TEXT,
)

from pythonforandroid.util import BuildInterruptingException

running_in_py2 = int(py_version[0]) < 3


class TestRecommendations(unittest.TestCase):
    """
    An inherited class of `unittest.TestCase`to test the module
    :mod:`~pythonforandroid.recommendations`.
    """

    def setUp(self):
        self.ndk_dir = "/opt/android/android-ndk"

    @unittest.skipIf(running_in_py2, "`assertLogs` requires Python 3.4+")
    @mock.patch("pythonforandroid.recommendations.read_ndk_version")
    def test_check_ndk_version_greater_than_recommended(self, mock_read_ndk):
        _version_string = f"{MIN_NDK_VERSION + 1}.0.5232133"
        mock_read_ndk.return_value = packaging.version.Version(_version_string)
        with self.assertLogs(level="INFO") as cm:
            check_ndk_version(self.ndk_dir)
        mock_read_ndk.assert_called_once_with(self.ndk_dir)
        self.assertEqual(
            cm.output,
            [
                "INFO:p4a:[INFO]:    {}".format(
                    CURRENT_NDK_VERSION_MESSAGE.format(
                        ndk_version=MAX_NDK_VERSION + 1
                    )
                ),
                "WARNING:p4a:[WARNING]: {}".format(
                    RECOMMENDED_NDK_VERSION_MESSAGE.format(
                        recommended_ndk_version=RECOMMENDED_NDK_VERSION
                    )
                ),
                "WARNING:p4a:[WARNING]: {}".format(NEW_NDK_MESSAGE),
            ],
        )

    @mock.patch("pythonforandroid.recommendations.read_ndk_version")
    def test_check_ndk_version_lower_than_recommended(self, mock_read_ndk):
        _version_string = f"{MIN_NDK_VERSION - 1}.0.5232133"
        mock_read_ndk.return_value = packaging.version.Version(_version_string)
        with self.assertRaises(BuildInterruptingException) as e:
            check_ndk_version(self.ndk_dir)
        self.assertEqual(
            e.exception.args[0],
            NDK_LOWER_THAN_SUPPORTED_MESSAGE.format(
                min_supported=MIN_NDK_VERSION, ndk_url=NDK_DOWNLOAD_URL
            ),
        )
        mock_read_ndk.assert_called_once_with(self.ndk_dir)

    @unittest.skipIf(running_in_py2, "`assertLogs` requires Python 3.4+")
    def test_check_ndk_version_error(self):
        """
        Test that a fake ndk dir give us two messages:
            - first should be an `INFO` log
            - second should be an `WARNING` log
        """
        with self.assertLogs(level="INFO") as cm:
            check_ndk_version(self.ndk_dir)
        self.assertEqual(
            cm.output,
            [
                "INFO:p4a:[INFO]:    {}".format(UNKNOWN_NDK_MESSAGE),
                "WARNING:p4a:[WARNING]: {}".format(
                    READ_ERROR_NDK_MESSAGE.format(ndk_dir=self.ndk_dir)
                ),
                "WARNING:p4a:[WARNING]: {}".format(
                    ENSURE_RIGHT_NDK_MESSAGE.format(
                        min_supported=MIN_NDK_VERSION,
                        rec_version=RECOMMENDED_NDK_VERSION,
                        ndk_url=NDK_DOWNLOAD_URL,
                    )
                ),
            ],
        )

    @mock.patch("pythonforandroid.recommendations.open")
    def test_read_ndk_version(self, mock_open_src_prop):
        mock_open_src_prop.side_effect = [
            mock.mock_open(
                read_data="Pkg.Revision = 17.2.4988734"
            ).return_value
        ]
        version = read_ndk_version(self.ndk_dir)
        mock_open_src_prop.assert_called_once_with(
            join(self.ndk_dir, "source.properties")
        )
        assert version.major == 17
        assert version.minor == 2
        assert version.micro == 4988734

    @unittest.skipIf(running_in_py2, "`assertLogs` requires Python 3.4+")
    @mock.patch("pythonforandroid.recommendations.open")
    def test_read_ndk_version_error(self, mock_open_src_prop):
        mock_open_src_prop.side_effect = [
            mock.mock_open(read_data="").return_value
        ]
        with self.assertLogs(level="INFO") as cm:
            version = read_ndk_version(self.ndk_dir)
        self.assertEqual(
            cm.output,
            ["INFO:p4a:[INFO]:    {}".format(PARSE_ERROR_NDK_MESSAGE)],
        )
        mock_open_src_prop.assert_called_once_with(
            join(self.ndk_dir, "source.properties")
        )
        assert version is None

    def test_check_target_api_error_arch_armeabi(self):

        with self.assertRaises(BuildInterruptingException) as e:
            check_target_api(RECOMMENDED_TARGET_API, "armeabi")
        self.assertEqual(
            e.exception.args[0],
            UNSUPPORTED_NDK_API_FOR_ARMEABI_MESSAGE.format(
                req_ndk_api=RECOMMENDED_TARGET_API,
                max_ndk_api=ARMEABI_MAX_TARGET_API,
            ),
        )

    @unittest.skipIf(running_in_py2, "`assertLogs` requires Python 3.4+")
    def test_check_target_api_warning_target_api(self):

        with self.assertLogs(level="INFO") as cm:
            check_target_api(MIN_TARGET_API - 1, MIN_TARGET_API)
        self.assertEqual(
            cm.output,
            [
                "WARNING:p4a:[WARNING]: Target API 29 < 30",
                "WARNING:p4a:[WARNING]: {old_api_msg}".format(
                    old_api_msg=OLD_API_MESSAGE
                ),
            ],
        )

    def test_check_ndk_api_error_android_api(self):
        """
        Given an `android api` greater than an `ndk_api`, we should get an
        `BuildInterruptingException`.
        """
        ndk_api = MIN_NDK_API + 1
        android_api = MIN_NDK_API
        with self.assertRaises(BuildInterruptingException) as e:
            check_ndk_api(ndk_api, android_api)
        self.assertEqual(
            e.exception.args[0],
            TARGET_NDK_API_GREATER_THAN_TARGET_API_MESSAGE.format(
                ndk_api=ndk_api, android_api=android_api
            ),
        )

    @unittest.skipIf(running_in_py2, "`assertLogs` requires Python 3.4+")
    def test_check_ndk_api_warning_old_ndk(self):
        """
        Given an `android api` lower than the supported by p4a, we should
        get an `BuildInterruptingException`.
        """
        ndk_api = MIN_NDK_API - 1
        android_api = RECOMMENDED_TARGET_API
        with self.assertLogs(level="INFO") as cm:
            check_ndk_api(ndk_api, android_api)
        self.assertEqual(
            cm.output,
            [
                "WARNING:p4a:[WARNING]: {}".format(
                    OLD_NDK_API_MESSAGE.format(MIN_NDK_API)
                )
            ],
        )

    def test_check_python_version(self):
        """With any version info lower than the minimum, we should get a
        BuildInterruptingException with an appropriate message.
        """
        with mock.patch('sys.version_info') as fake_version_info:

            # Major version is Python 2 => exception
            fake_version_info.major = MIN_PYTHON_MAJOR_VERSION - 1
            fake_version_info.minor = MIN_PYTHON_MINOR_VERSION
            with self.assertRaises(BuildInterruptingException) as context:
                check_python_version()
            assert context.exception.message == PY2_ERROR_TEXT

            # Major version too low => exception
            # Using a float valued major version just to test the logic and avoid
            # clashing with the Python 2 check
            fake_version_info.major = MIN_PYTHON_MAJOR_VERSION - 0.1
            fake_version_info.minor = MIN_PYTHON_MINOR_VERSION
            with self.assertRaises(BuildInterruptingException) as context:
                check_python_version()
            assert context.exception.message == PY_VERSION_ERROR_TEXT

            # Minor version too low => exception
            fake_version_info.major = MIN_PYTHON_MAJOR_VERSION
            fake_version_info.minor = MIN_PYTHON_MINOR_VERSION - 1
            with self.assertRaises(BuildInterruptingException) as context:
                check_python_version()
            assert context.exception.message == PY_VERSION_ERROR_TEXT

            # Version high enough => nothing interesting happens
            fake_version_info.major = MIN_PYTHON_MAJOR_VERSION
            fake_version_info.minor = MIN_PYTHON_MINOR_VERSION
            check_python_version()

    def test_print_recommendations(self):
        """
        Simple test that the function actually runs.
        """
        # The main failure mode is if the function tries to print a variable
        # that doesn't actually exist, so simply running to check all the
        # prints work is the most important test.
        print_recommendations()
