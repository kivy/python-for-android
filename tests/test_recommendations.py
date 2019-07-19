import unittest
from os.path import join
from sys import version as py_version

try:
    from unittest import mock
except ImportError:
    # `Python 2` or lower than `Python 3.3` does not
    # have the `unittest.mock` module built-in
    import mock
from pythonforandroid.recommendations import (
    check_ndk_api,
    check_ndk_version,
    check_target_api,
    read_ndk_version,
    MAX_NDK_VERSION,
    RECOMMENDED_NDK_VERSION,
    RECOMMENDED_TARGET_API,
    MIN_NDK_API,
    MIN_NDK_VERSION,
    NDK_DOWNLOAD_URL,
    ARMEABI_MAX_TARGET_API,
    MIN_TARGET_API,
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
        mock_read_ndk.return_value.version = [MAX_NDK_VERSION + 1, 0, 5232133]
        with self.assertLogs(level="INFO") as cm:
            check_ndk_version(self.ndk_dir)
        mock_read_ndk.assert_called_once_with(self.ndk_dir)
        self.assertEqual(
            cm.output,
            [
                "INFO:p4a:[INFO]:    Found NDK version {ndk_current}".format(
                    ndk_current=MAX_NDK_VERSION + 1
                ),
                "WARNING:p4a:[WARNING]:"
                " Maximum recommended NDK version is {ndk_recommended}".format(
                    ndk_recommended=RECOMMENDED_NDK_VERSION
                ),
                "WARNING:p4a:[WARNING]:"
                " Newer NDKs may not be fully supported by p4a.",
            ],
        )

    @mock.patch("pythonforandroid.recommendations.read_ndk_version")
    def test_check_ndk_version_lower_than_recommended(self, mock_read_ndk):
        mock_read_ndk.return_value.version = [MIN_NDK_VERSION - 1, 0, 5232133]
        with self.assertRaises(BuildInterruptingException) as e:
            check_ndk_version(self.ndk_dir)
        self.assertEqual(
            e.exception.args[0],
            "Unsupported NDK version detected {ndk_current}"
            "\n* Note: Minimum supported NDK version is {ndk_min}".format(
                ndk_current=MIN_NDK_VERSION - 1, ndk_min=MIN_NDK_VERSION
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
                "INFO:p4a:[INFO]:    Could not determine NDK version, "
                "no source.properties in the NDK dir",
                "WARNING:p4a:[WARNING]: Unable to read the ndk version, "
                "assuming that you are using an NDK greater than 17 (the "
                "minimum ndk required to use p4a successfully).\n"
                "Note: If you got build errors, consider to download the "
                "recommended ndk version which is 17c and try it again (after "
                "removing all the files generated with this build). To "
                "download the android NDK visit the following "
                "page: {download_url}".format(download_url=NDK_DOWNLOAD_URL),
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
        assert version == "17.2.4988734"

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
            [
                "INFO:p4a:[INFO]:    Could not parse "
                "$NDK_DIR/source.properties, not checking NDK version"
            ],
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
            "Asked to build for armeabi architecture with API {ndk_api}, but "
            "API {max_target_api} or greater does not support armeabi".format(
                ndk_api=RECOMMENDED_TARGET_API,
                max_target_api=ARMEABI_MAX_TARGET_API,
            ),
        )

    @unittest.skipIf(running_in_py2, "`assertLogs` requires Python 3.4+")
    def test_check_target_api_warning_target_api(self):

        with self.assertLogs(level="INFO") as cm:
            check_target_api(MIN_TARGET_API - 1, MIN_TARGET_API)
        self.assertEqual(
            cm.output,
            [
                "WARNING:p4a:[WARNING]: Target API 25 < 26",
                "WARNING:p4a:[WARNING]: Target APIs lower than 26 are no "
                "longer supported on Google Play, and are not recommended. "
                "Note that the Target API can be higher than your device "
                "Android version, and should usually be as high as possible.",
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
            "Target NDK API is {ndk_api}, higher than the target Android "
            "API {android_api}.".format(
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
            ["WARNING:p4a:[WARNING]: NDK API less than 21 is not supported"],
        )
