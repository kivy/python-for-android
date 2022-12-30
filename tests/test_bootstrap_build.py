import unittest
import pytest
import os
import argparse

from pythonforandroid.util import load_source


class TestParsePermissions(unittest.TestCase):
    def test_parse_permissions_with_migrations(self):
        # Test that permissions declared in the old format are migrated to the
        # new format.
        # (Users can new declare permissions in both formats, even a mix)
        os.environ["P4A_BUILD_IS_RUNNING_UNITTESTS"] = "1"

        ap = argparse.ArgumentParser()
        ap.add_argument(
            "--permission",
            dest="permissions",
            action="append",
            default=[],
            help="The permissions to give this app.",
            nargs="+",
        )

        args = [
            "--permission",
            "INTERNET",
            "--permission",
            "com.android.voicemail.permission.ADD_VOICEMAIL",
            "--permission",
            "(name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=18)",
            "--permission",
            "(name=android.permission.BLUETOOTH_SCAN;usesPermissionFlags=neverForLocation)",
        ]

        args = ap.parse_args(args)

        build_src = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../pythonforandroid/bootstraps/common/build/build.py",
        )

        buildpy = load_source("buildpy", build_src)
        parsed_permissions = buildpy.parse_permissions(args.permissions)

        assert parsed_permissions == [
            dict(name="android.permission.INTERNET"),
            dict(name="com.android.voicemail.permission.ADD_VOICEMAIL"),
            dict(name="android.permission.WRITE_EXTERNAL_STORAGE", maxSdkVersion="18"),
            dict(
                name="android.permission.BLUETOOTH_SCAN",
                usesPermissionFlags="neverForLocation",
            ),
        ]

    def test_parse_permissions_invalid_property(self):
        os.environ["P4A_BUILD_IS_RUNNING_UNITTESTS"] = "1"

        ap = argparse.ArgumentParser()
        ap.add_argument(
            "--permission",
            dest="permissions",
            action="append",
            default=[],
            help="The permissions to give this app.",
            nargs="+",
        )

        args = [
            "--permission",
            "(name=android.permission.BLUETOOTH_SCAN;propertyThatFails=neverForLocation)",
        ]

        args = ap.parse_args(args)

        build_src = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../pythonforandroid/bootstraps/common/build/build.py",
        )

        buildpy = load_source("buildpy", build_src)

        with pytest.raises(
            ValueError, match="Property 'propertyThatFails' is not supported."
        ):
            buildpy.parse_permissions(args.permissions)
