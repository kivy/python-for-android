import unittest
from unittest import mock
import pytest
import os

from pythonforandroid.util import load_source


class TestBootstrapBuild(unittest.TestCase):
    def setUp(self):
        os.environ["P4A_BUILD_IS_RUNNING_UNITTESTS"] = "1"

        build_src = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "../pythonforandroid/bootstraps/common/build/build.py",
        )

        self.buildpy = load_source("buildpy", build_src)
        self.buildpy.get_bootstrap_name = mock.Mock(return_value="sdl2")

        self.ap = self.buildpy.create_argument_parser()

        self.common_args = [
            "--package",
            "org.test.app",
            "--name",
            "TestApp",
            "--version",
            "0.1",
        ]


class TestParsePermissions(TestBootstrapBuild):
    def test_parse_permissions_with_migrations(self):
        # Test that permissions declared in the old format are migrated to the
        # new format.
        # (Users can new declare permissions in both formats, even a mix)

        self.ap = self.buildpy.create_argument_parser()

        args = [
            *self.common_args,
            "--permission",
            "INTERNET",
            "--permission",
            "com.android.voicemail.permission.ADD_VOICEMAIL",
            "--permission",
            "(name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=18)",
            "--permission",
            "(name=android.permission.BLUETOOTH_SCAN;usesPermissionFlags=neverForLocation)",
        ]

        args = self.ap.parse_args(args)

        parsed_permissions = self.buildpy.parse_permissions(args.permissions)

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

        self.ap = self.buildpy.create_argument_parser()

        args = [
            *self.common_args,
            "--permission",
            "(name=android.permission.BLUETOOTH_SCAN;propertyThatFails=neverForLocation)",
        ]

        args = self.ap.parse_args(args)

        with pytest.raises(
            ValueError, match="Property 'propertyThatFails' is not supported."
        ):
            self.buildpy.parse_permissions(args.permissions)


class TestOrientationArg(TestBootstrapBuild):
    def test_no_orientation_args(self):

        args = self.common_args

        args = self.ap.parse_args(args)

        assert (
            self.buildpy.get_manifest_orientation(
                args.orientation, args.manifest_orientation
            )
            == "unspecified"
        )
        assert self.buildpy.get_sdl_orientation_hint(args.orientation) == ""

    def test_manifest_orientation_present(self):

        args = [
            *self.common_args,
            "--orientation",
            "landscape",
            "--orientation",
            "portrait",
            "--manifest-orientation",
            "fullSensor",
        ]

        args = self.ap.parse_args(args)

        assert (
            self.buildpy.get_manifest_orientation(
                args.orientation, manifest_orientation=args.manifest_orientation
            )
            == "fullSensor"
        )

    def test_manifest_orientation_supported(self):

        args = [*self.common_args, "--orientation", "landscape"]

        args = self.ap.parse_args(args)

        assert (
            self.buildpy.get_manifest_orientation(
                args.orientation, manifest_orientation=args.manifest_orientation
            )
            == "landscape"
        )

    def test_android_manifest_multiple_orientation_supported(self):

        args = [
            *self.common_args,
            "--orientation",
            "landscape",
            "--orientation",
            "portrait",
        ]

        args = self.ap.parse_args(args)

        assert (
            self.buildpy.get_manifest_orientation(
                args.orientation, manifest_orientation=args.manifest_orientation
            )
            == "unspecified"
        )

    def test_sdl_orientation_hint_single(self):

        args = [*self.common_args, "--orientation", "landscape"]

        args = self.ap.parse_args(args)

        assert (
            self.buildpy.get_sdl_orientation_hint(args.orientation) == "LandscapeLeft"
        )

    def test_sdl_orientation_hint_multiple(self):

        args = [
            *self.common_args,
            "--orientation",
            "landscape",
            "--orientation",
            "portrait",
        ]

        args = self.ap.parse_args(args)

        sdl_orientation_hint = self.buildpy.get_sdl_orientation_hint(
            args.orientation
        ).split(" ")

        assert "LandscapeLeft" in sdl_orientation_hint
        assert "Portrait" in sdl_orientation_hint
