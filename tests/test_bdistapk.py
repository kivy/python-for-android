import sys
from unittest import mock
from setuptools.dist import Distribution

from pythonforandroid.bdistapk import (
    argv_contains,
    BdistAPK,
    BdistAAR,
    BdistAAB,
)


class TestArgvContains:
    """Test argv_contains helper function."""

    def test_argv_contains_present(self):
        """Test argv_contains returns True when argument is present."""
        with mock.patch.object(sys, 'argv', ['prog', '--name=test', '--version=1.0']):
            assert argv_contains('--name')
            assert argv_contains('--version')

    def test_argv_contains_partial_match(self):
        """Test argv_contains returns True for partial matches."""
        with mock.patch.object(sys, 'argv', ['prog', '--name=test']):
            assert argv_contains('--name')
            assert argv_contains('--nam')

    def test_argv_contains_not_present(self):
        """Test argv_contains returns False when argument is not present."""
        with mock.patch.object(sys, 'argv', ['prog', '--name=test']):
            assert not argv_contains('--package')
            assert not argv_contains('--arch')


class TestBdist:
    """Test Bdist base class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.distribution = Distribution({
            'name': 'TestApp',
            'version': '1.0.0',
        })
        self.distribution.package_data = {'testapp': ['*.py', '*.kv']}

    @mock.patch('pythonforandroid.bdistapk.ensure_dir')
    @mock.patch('pythonforandroid.bdistapk.rmdir')
    def test_initialize_options(self, mock_rmdir, mock_ensure_dir):
        """Test initialize_options sets attributes from user_options."""
        bdist = BdistAPK(self.distribution)
        bdist.user_options = [('name=', None, None), ('version=', None, None)]

        bdist.initialize_options()

        assert hasattr(bdist, 'name')
        assert hasattr(bdist, 'version')

    @mock.patch('pythonforandroid.bdistapk.argv_contains')
    @mock.patch('pythonforandroid.bdistapk.ensure_dir')
    @mock.patch('pythonforandroid.bdistapk.rmdir')
    def test_finalize_options_injects_defaults(
        self, mock_rmdir, mock_ensure_dir, mock_argv_contains
    ):
        """Test finalize_options injects default name, package, version, arch."""
        mock_argv_contains.return_value = False

        with mock.patch.object(sys, 'argv', ['setup.py', 'apk']):
            bdist = BdistAPK(self.distribution)
            bdist.finalize_options()

            # Check that defaults were added to sys.argv
            argv_str = ' '.join(sys.argv)
            assert '--name=' in argv_str or any('--name' in arg for arg in sys.argv)

    @mock.patch('pythonforandroid.bdistapk.argv_contains')
    @mock.patch('pythonforandroid.bdistapk.ensure_dir')
    @mock.patch('pythonforandroid.bdistapk.rmdir')
    def test_finalize_options_permissions_handling(
        self, mock_rmdir, mock_ensure_dir, mock_argv_contains
    ):
        """Test finalize_options handles permissions list correctly."""
        mock_argv_contains.side_effect = lambda x: x != '--permissions'

        # Set up permissions in the distribution command options
        self.distribution.command_options['apk'] = {
            'permissions': ('setup.py', ['INTERNET', 'CAMERA'])
        }

        with mock.patch.object(sys, 'argv', ['setup.py', 'apk']):
            bdist = BdistAPK(self.distribution)
            bdist.package_type = 'apk'
            bdist.finalize_options()

            # Check permissions were added
            assert any('--permission=INTERNET' in arg for arg in sys.argv)
            assert any('--permission=CAMERA' in arg for arg in sys.argv)

    @mock.patch('pythonforandroid.entrypoints.main')
    @mock.patch('pythonforandroid.bdistapk.argv_contains')
    @mock.patch('pythonforandroid.bdistapk.ensure_dir')
    @mock.patch('pythonforandroid.bdistapk.rmdir')
    @mock.patch('pythonforandroid.bdistapk.copyfile')
    @mock.patch('pythonforandroid.bdistapk.glob')
    def test_run_calls_main(
        self, mock_glob, mock_copyfile, mock_rmdir, mock_ensure_dir,
        mock_argv_contains, mock_main
    ):
        """Test run() calls prepare_build_dir and then main()."""
        mock_glob.return_value = ['testapp/main.py']
        mock_argv_contains.return_value = False  # Not using --launcher or --private

        with mock.patch.object(sys, 'argv', ['setup.py', 'apk']):
            bdist = BdistAPK(self.distribution)
            bdist.arch = 'armeabi-v7a'
            bdist.run()

            mock_rmdir.assert_called()
            mock_ensure_dir.assert_called()
            mock_main.assert_called_once()
            assert sys.argv[1] == 'apk'

    @mock.patch('pythonforandroid.bdistapk.argv_contains')
    @mock.patch('pythonforandroid.bdistapk.ensure_dir')
    @mock.patch('pythonforandroid.bdistapk.rmdir')
    @mock.patch('pythonforandroid.bdistapk.copyfile')
    @mock.patch('pythonforandroid.bdistapk.glob')
    @mock.patch('builtins.exit', side_effect=SystemExit(1))
    def test_prepare_build_dir_no_main_py(
        self, mock_exit, mock_glob, mock_copyfile,
        mock_rmdir, mock_ensure_dir, mock_argv_contains
    ):
        """Test prepare_build_dir exits if no main.py found and not using launcher."""
        mock_glob.return_value = ['testapp/helper.py']
        mock_argv_contains.return_value = False  # Not using --launcher

        bdist = BdistAPK(self.distribution)
        bdist.arch = 'armeabi-v7a'

        # Expect SystemExit to be raised
        try:
            bdist.prepare_build_dir()
            assert False, "Expected SystemExit to be raised"
        except SystemExit:
            pass

        mock_exit.assert_called_once_with(1)

    @mock.patch('pythonforandroid.bdistapk.argv_contains')
    @mock.patch('pythonforandroid.bdistapk.ensure_dir')
    @mock.patch('pythonforandroid.bdistapk.rmdir')
    @mock.patch('pythonforandroid.bdistapk.copyfile')
    @mock.patch('pythonforandroid.bdistapk.glob')
    def test_prepare_build_dir_with_main_py(
        self, mock_glob, mock_copyfile, mock_rmdir,
        mock_ensure_dir, mock_argv_contains
    ):
        """Test prepare_build_dir succeeds when main.py is found."""
        mock_glob.return_value = ['testapp/main.py', 'testapp/helper.py']
        # Return False for all argv_contains checks (no --launcher, no --private)
        mock_argv_contains.return_value = False

        with mock.patch.object(sys, 'argv', ['setup.py', 'apk']):
            bdist = BdistAPK(self.distribution)
            bdist.arch = 'armeabi-v7a'
            bdist.prepare_build_dir()

            # Should have copied files (glob might return duplicates)
            assert mock_copyfile.call_count >= 2
            # Should have added --private argument
            assert any('--private=' in arg for arg in sys.argv)


class TestBdistSubclasses:
    """Test BdistAPK, BdistAAR, BdistAAB subclasses."""

    def setup_method(self):
        """Set up test fixtures."""
        self.distribution = Distribution({
            'name': 'TestApp',
            'version': '1.0.0',
        })
        self.distribution.package_data = {}

    def test_bdist_apk_package_type(self):
        """Test BdistAPK has correct package_type."""
        bdist = BdistAPK(self.distribution)
        assert bdist.package_type == 'apk'
        assert bdist.description == 'Create an APK with python-for-android'

    def test_bdist_aar_package_type(self):
        """Test BdistAAR has correct package_type."""
        bdist = BdistAAR(self.distribution)
        assert bdist.package_type == 'aar'
        assert bdist.description == 'Create an AAR with python-for-android'

    def test_bdist_aab_package_type(self):
        """Test BdistAAB has correct package_type."""
        bdist = BdistAAB(self.distribution)
        assert bdist.package_type == 'aab'
        assert bdist.description == 'Create an AAB with python-for-android'
