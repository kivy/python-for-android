from unittest import mock

from pythonforandroid.patching import (
    is_platform,
    is_linux,
    is_darwin,
    is_windows,
    is_arch,
    is_api,
    is_api_gt,
    is_api_gte,
    is_api_lt,
    is_api_lte,
    is_ndk,
    is_version_gt,
    is_version_lt,
    version_starts_with,
    will_build,
    check_all,
    check_any,
)


class TestPlatformChecks:
    """Test platform detection functions."""

    @mock.patch('pythonforandroid.patching.uname')
    def test_is_platform_linux(self, mock_uname):
        """Test is_platform returns check function for Linux."""
        mock_uname.return_value = mock.Mock(system='Linux')
        check_fn = is_platform('Linux')
        assert check_fn(None, None)

    @mock.patch('pythonforandroid.patching.uname')
    def test_is_platform_darwin(self, mock_uname):
        """Test is_platform returns check function for Darwin."""
        mock_uname.return_value = mock.Mock(system='Darwin')
        check_fn = is_platform('Darwin')
        assert check_fn(None, None)

    @mock.patch('pythonforandroid.patching.uname')
    def test_is_platform_case_insensitive(self, mock_uname):
        """Test is_platform is case insensitive."""
        mock_uname.return_value = mock.Mock(system='LINUX')
        check_fn = is_platform('linux')
        assert check_fn(None, None)

    @mock.patch('pythonforandroid.patching.uname')
    def test_is_platform_mismatch(self, mock_uname):
        """Test is_platform returns False for mismatched platform."""
        mock_uname.return_value = mock.Mock(system='Linux')
        check_fn = is_platform('Windows')
        assert not check_fn(None, None)

    def test_is_linux(self):
        """Test is_linux constant function is defined."""
        # is_linux is defined at module import time based on real platform
        # We can only verify it's callable
        assert callable(is_linux)

    def test_is_darwin(self):
        """Test is_darwin constant function is defined."""
        # is_darwin is defined at module import time based on real platform
        # We can only verify it's callable
        assert callable(is_darwin)

    def test_is_windows(self):
        """Test is_windows constant function is defined."""
        # is_windows is defined at module import time based on real platform
        # We can only verify it's callable
        assert callable(is_windows)


class TestArchChecks:
    """Test architecture check functions."""

    def test_is_arch_match(self):
        """Test is_arch returns True for matching architecture."""
        mock_arch = mock.Mock(arch='armeabi-v7a')
        check_fn = is_arch('armeabi-v7a')
        assert check_fn(mock_arch)

    def test_is_arch_mismatch(self):
        """Test is_arch returns False for mismatched architecture."""
        mock_arch = mock.Mock(arch='armeabi-v7a')
        check_fn = is_arch('arm64-v8a')
        assert not check_fn(mock_arch)


class TestAndroidAPIChecks:
    """Test Android API level comparison functions."""

    def test_is_api_equal(self):
        """Test is_api for equal API level."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.android_api = 21
        check_fn = is_api(21)
        assert check_fn(None, mock_recipe)

    def test_is_api_not_equal(self):
        """Test is_api for unequal API level."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.android_api = 21
        check_fn = is_api(27)
        assert not check_fn(None, mock_recipe)

    def test_is_api_gt(self):
        """Test is_api_gt for greater than comparison."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.android_api = 27
        check_fn = is_api_gt(21)
        assert check_fn(None, mock_recipe)

        mock_recipe.ctx.android_api = 21
        assert not check_fn(None, mock_recipe)

    def test_is_api_gte(self):
        """Test is_api_gte for greater than or equal comparison."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.android_api = 27
        check_fn = is_api_gte(21)
        assert check_fn(None, mock_recipe)

        mock_recipe.ctx.android_api = 21
        check_fn = is_api_gte(21)
        assert check_fn(None, mock_recipe)

        mock_recipe.ctx.android_api = 19
        assert not check_fn(None, mock_recipe)

    def test_is_api_lt(self):
        """Test is_api_lt for less than comparison."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.android_api = 19
        check_fn = is_api_lt(21)
        assert check_fn(None, mock_recipe)

        mock_recipe.ctx.android_api = 21
        assert not check_fn(None, mock_recipe)

    def test_is_api_lte(self):
        """Test is_api_lte for less than or equal comparison."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.android_api = 19
        check_fn = is_api_lte(21)
        assert check_fn(None, mock_recipe)

        mock_recipe.ctx.android_api = 21
        check_fn = is_api_lte(21)
        assert check_fn(None, mock_recipe)

        mock_recipe.ctx.android_api = 27
        assert not check_fn(None, mock_recipe)


class TestNDKChecks:
    """Test NDK version check functions."""

    def test_is_ndk_equal(self):
        """Test is_ndk for equal NDK version."""
        mock_ndk = mock.Mock(name='ndk_r21e')
        mock_recipe = mock.Mock()
        mock_recipe.ctx.ndk = mock_ndk
        check_fn = is_ndk(mock_ndk)
        assert check_fn(None, mock_recipe)

    def test_is_ndk_not_equal(self):
        """Test is_ndk for unequal NDK version."""
        mock_ndk1 = mock.Mock(name='ndk_r21e')
        mock_ndk2 = mock.Mock(name='ndk_r25c')
        mock_recipe = mock.Mock()
        mock_recipe.ctx.ndk = mock_ndk1
        check_fn = is_ndk(mock_ndk2)
        assert not check_fn(None, mock_recipe)


class TestVersionChecks:
    """Test recipe version comparison functions."""

    def test_is_version_gt(self):
        """Test is_version_gt for version comparison."""
        mock_recipe = mock.Mock(version='2.0.0')
        check_fn = is_version_gt('1.0.0')
        assert check_fn(None, mock_recipe)

        mock_recipe.version = '1.0.0'
        assert not check_fn(None, mock_recipe)

    def test_is_version_lt(self):
        """Test is_version_lt for version comparison."""
        mock_recipe = mock.Mock(version='1.0.0')
        check_fn = is_version_lt('2.0.0')
        assert check_fn(None, mock_recipe)

        mock_recipe.version = '2.0.0'
        assert not check_fn(None, mock_recipe)

    def test_version_starts_with(self):
        """Test version_starts_with for version prefix matching."""
        mock_recipe = mock.Mock(version='1.15.2')
        check_fn = version_starts_with('1.15')
        assert check_fn(None, mock_recipe)

        check_fn = version_starts_with('1.14')
        assert not check_fn(None, mock_recipe)

        check_fn = version_starts_with('2')
        assert not check_fn(None, mock_recipe)


class TestWillBuild:
    """Test will_build function."""

    def test_will_build_present(self):
        """Test will_build returns True when recipe is in build order."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.recipe_build_order = ['python3', 'numpy', 'kivy']
        check_fn = will_build('numpy')
        assert check_fn(None, mock_recipe)

    def test_will_build_absent(self):
        """Test will_build returns False when recipe is not in build order."""
        mock_recipe = mock.Mock()
        mock_recipe.ctx.recipe_build_order = ['python3', 'numpy', 'kivy']
        check_fn = will_build('scipy')
        assert not check_fn(None, mock_recipe)


class TestConjunctions:
    """Test logical conjunction functions."""

    def test_check_all_all_true(self):
        """Test check_all returns True when all checks pass."""
        def check1(_arch, _recipe):
            return True

        def check2(_arch, _recipe):
            return True

        def check3(_arch, _recipe):
            return True

        check_fn = check_all(check1, check2, check3)
        assert check_fn(None, None)

    def test_check_all_one_false(self):
        """Test check_all returns False when one check fails."""
        def check1(_arch, _recipe):
            return True

        def check2(_arch, _recipe):
            return False

        def check3(_arch, _recipe):
            return True

        check_fn = check_all(check1, check2, check3)
        assert not check_fn(None, None)

    def test_check_all_all_false(self):
        """Test check_all returns False when all checks fail."""
        def check1(_arch, _recipe):
            return False

        def check2(_arch, _recipe):
            return False

        check_fn = check_all(check1, check2)
        assert not check_fn(None, None)

    def test_check_any_one_true(self):
        """Test check_any returns True when one check passes."""
        def check1(_arch, _recipe):
            return False

        def check2(_arch, _recipe):
            return True

        def check3(_arch, _recipe):
            return False

        check_fn = check_any(check1, check2, check3)
        assert check_fn(None, None)

    def test_check_any_all_false(self):
        """Test check_any returns False when all checks fail."""
        def check1(_arch, _recipe):
            return False

        def check2(_arch, _recipe):
            return False

        check_fn = check_any(check1, check2)
        assert not check_fn(None, None)

    def test_check_any_all_true(self):
        """Test check_any returns True when all checks pass."""
        def check1(_arch, _recipe):
            return True

        def check2(_arch, _recipe):
            return True

        check_fn = check_any(check1, check2)
        assert check_fn(None, None)

    @mock.patch('pythonforandroid.patching.uname')
    def test_combined_checks(self, mock_uname):
        """Test combining multiple check functions with check_all and check_any."""
        # Test check_all with is_platform and is_version_gt
        mock_uname.return_value = mock.Mock(system='Linux')
        mock_recipe = mock.Mock(version='2.0.0')

        check_fn = check_all(
            is_platform('Linux'),
            is_version_gt('1.0.0')
        )
        assert check_fn(None, mock_recipe)

        # Test check_any with is_platform and is_version_gt
        mock_uname.return_value = mock.Mock(system='Windows')
        check_fn = check_any(
            is_platform('Linux'),
            is_version_gt('1.0.0')
        )
        assert check_fn(None, mock_recipe)
