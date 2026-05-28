import unittest
from unittest import mock
import pytest
import os

from pythonforandroid.util import load_source


def load_bootstrap_build_module():
    os.environ["P4A_BUILD_IS_RUNNING_UNITTESTS"] = "1"

    build_src = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "../pythonforandroid/bootstraps/common/build/build.py",
    )

    buildpy = load_source("buildpy", build_src)
    buildpy.get_bootstrap_name = mock.Mock(return_value="sdl2")
    return buildpy


class TestBootstrapBuild(unittest.TestCase):
    def setUp(self):
        self.buildpy = load_bootstrap_build_module()
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


class TestAndroidNumericVersion:
    def setup_method(self):
        self.buildpy = load_bootstrap_build_module()

    def test_generates_default_three_part_version_code(self):
        assert self.buildpy.get_android_numeric_version("1.0.5", 24) == "102410005"

    def test_accepts_and_normalizes_explicit_numeric_version(self):
        assert self.buildpy.validate_android_numeric_version("0000001") == "1"
        assert self.buildpy.validate_android_numeric_version(2100000000) == "2100000000"

    @pytest.mark.parametrize("numeric_version", ["abc", "1.2", "", None])
    def test_rejects_non_integer_explicit_numeric_versions(self, numeric_version):
        with pytest.raises(ValueError, match="--numeric-version.*decimal integer"):
            self.buildpy.validate_android_numeric_version(numeric_version)

    @pytest.mark.parametrize("numeric_version", ["0", 0, "-1", -1])
    def test_rejects_non_positive_explicit_numeric_versions(self, numeric_version):
        with pytest.raises(ValueError, match="--numeric-version.*greater than 0"):
            self.buildpy.validate_android_numeric_version(numeric_version)

    @pytest.mark.parametrize("numeric_version", ["2100000001", 2100000001])
    def test_rejects_oversized_explicit_numeric_versions(self, numeric_version):
        with pytest.raises(
            ValueError, match="--numeric-version.*2100000000"
        ):
            self.buildpy.validate_android_numeric_version(numeric_version)

    def test_rejects_generated_overflow_and_mentions_version_name(self):
        generated_version = self.buildpy.get_android_numeric_version("1.0.5.1", 24)

        with pytest.raises(
            ValueError,
            match="Generated Android versionCode .*--version '1\\.0\\.5\\.1'.*--numeric-version.*2100000000",
        ):
            self.buildpy.validate_android_numeric_version(
                generated_version, generated_from_version="1.0.5.1"
            )

    def test_rejects_non_numeric_version_name_for_generation(self):
        with pytest.raises(
            ValueError,
            match="Could not generate Android versionCode from --version '1\\.0\\.beta'.*versionName.*--numeric-version",
        ):
            self.buildpy.get_android_numeric_version("1.0.beta", 24)
