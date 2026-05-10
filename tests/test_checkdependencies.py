import sys
from unittest import mock

from pythonforandroid import checkdependencies


class TestCheckPythonDependencies:
    """Test check_python_dependencies function."""

    @mock.patch('pythonforandroid.checkdependencies.import_module')
    def test_all_modules_present(self, mock_import):
        """Test that check_python_dependencies completes when all modules are present."""
        # Mock all required modules
        mock_colorama = mock.Mock()
        mock_colorama.__version__ = '0.4.0'
        mock_sh = mock.Mock()
        mock_sh.__version__ = '1.12'
        mock_appdirs = mock.Mock()
        mock_jinja2 = mock.Mock()

        def import_side_effect(name):
            if name == 'colorama':
                return mock_colorama
            elif name == 'sh':
                return mock_sh
            elif name == 'appdirs':
                return mock_appdirs
            elif name == 'jinja2':
                return mock_jinja2
            raise ImportError(f"No module named '{name}'")

        mock_import.side_effect = import_side_effect

        with mock.patch.object(sys, 'modules', {
            'colorama': mock_colorama,
            'sh': mock_sh,
            'appdirs': mock_appdirs,
            'jinja2': mock_jinja2
        }):
            checkdependencies.check_python_dependencies()

    @mock.patch('builtins.exit')
    @mock.patch('builtins.print')
    @mock.patch('pythonforandroid.checkdependencies.import_module')
    def test_missing_module_without_version(self, mock_import, mock_print, mock_exit):
        """Test error message when module without version requirement is missing."""
        modules_dict = {}

        def import_side_effect(name):
            if name == 'appdirs':
                raise ImportError(f"No module named '{name}'")
            mock_mod = mock.Mock()
            mock_mod.__version__ = '1.0'
            modules_dict[name] = mock_mod
            return mock_mod

        mock_import.side_effect = import_side_effect

        with mock.patch.object(sys, 'modules', modules_dict):
            checkdependencies.check_python_dependencies()

        # Verify error message was printed
        error_calls = [str(call) for call in mock_print.call_args_list]
        assert any('appdirs' in call and 'ERROR' in call for call in error_calls)
        mock_exit.assert_called_once_with(1)

    @mock.patch('builtins.exit')
    @mock.patch('builtins.print')
    @mock.patch('pythonforandroid.checkdependencies.import_module')
    def test_missing_module_with_version(self, mock_import, mock_print, mock_exit):
        """Test error message when module with version requirement is missing."""
        modules_dict = {}

        def import_side_effect(name):
            if name == 'colorama':
                raise ImportError(f"No module named '{name}'")
            mock_mod = mock.Mock()
            mock_mod.__version__ = '1.0'
            modules_dict[name] = mock_mod
            return mock_mod

        mock_import.side_effect = import_side_effect

        with mock.patch.object(sys, 'modules', modules_dict):
            checkdependencies.check_python_dependencies()

        # Verify error message includes version requirement
        error_calls = [str(call) for call in mock_print.call_args_list]
        assert any('colorama' in call and '0.3.3' in call for call in error_calls)
        mock_exit.assert_called_once_with(1)

    @mock.patch('builtins.exit')
    @mock.patch('builtins.print')
    @mock.patch('pythonforandroid.checkdependencies.import_module')
    def test_module_version_too_old(self, mock_import, mock_print, mock_exit):
        """Test error when module version is too old."""
        mock_colorama = mock.Mock()
        mock_colorama.__version__ = '0.2.0'  # Too old, needs 0.3.3
        modules_dict = {'colorama': mock_colorama}

        def import_side_effect(name):
            if name == 'colorama':
                return mock_colorama
            mock_mod = mock.Mock()
            mock_mod.__version__ = '1.0'
            modules_dict[name] = mock_mod
            return mock_mod

        mock_import.side_effect = import_side_effect

        with mock.patch.object(sys, 'modules', modules_dict):
            checkdependencies.check_python_dependencies()

        # Verify error message about version
        error_calls = [str(call) for call in mock_print.call_args_list]
        assert any('version' in call.lower() and 'colorama' in call for call in error_calls)
        mock_exit.assert_called_once_with(1)

    @mock.patch('pythonforandroid.checkdependencies.import_module')
    def test_module_version_acceptable(self, mock_import):
        """Test that acceptable versions pass."""
        mock_colorama = mock.Mock()
        mock_colorama.__version__ = '0.4.0'  # Newer than 0.3.3
        mock_sh = mock.Mock()
        mock_sh.__version__ = '1.12'  # Newer than 1.10

        def import_side_effect(name):
            if name == 'colorama':
                return mock_colorama
            elif name == 'sh':
                return mock_sh
            mock_mod = mock.Mock()
            return mock_mod

        mock_import.side_effect = import_side_effect

        with mock.patch.object(sys, 'modules', {
            'colorama': mock_colorama,
            'sh': mock_sh
        }):
            # Should complete without error
            checkdependencies.check_python_dependencies()

    @mock.patch('pythonforandroid.checkdependencies.import_module')
    def test_module_without_version_attribute(self, mock_import):
        """Test handling of modules that don't have __version__."""
        mock_colorama = mock.Mock(spec=[])  # No __version__ attribute
        modules_dict = {'colorama': mock_colorama}

        def import_side_effect(name):
            if name == 'colorama':
                return mock_colorama
            mock_mod = mock.Mock()
            modules_dict[name] = mock_mod
            return mock_mod

        mock_import.side_effect = import_side_effect

        with mock.patch.object(sys, 'modules', modules_dict):
            # Should complete without error (version check is skipped)
            checkdependencies.check_python_dependencies()


class TestCheck:
    """Test the main check() function."""

    @mock.patch('pythonforandroid.checkdependencies.check_python_dependencies')
    @mock.patch('pythonforandroid.checkdependencies.check_and_install_default_prerequisites')
    def test_check_with_skip_prerequisites(self, mock_prereqs, mock_python_deps):
        """Test check() skips prerequisites when SKIP_PREREQUISITES_CHECK=1."""
        with mock.patch.dict('os.environ', {'SKIP_PREREQUISITES_CHECK': '1'}):
            checkdependencies.check()

        mock_prereqs.assert_not_called()
        mock_python_deps.assert_called_once()

    @mock.patch('pythonforandroid.checkdependencies.check_python_dependencies')
    @mock.patch('pythonforandroid.checkdependencies.check_and_install_default_prerequisites')
    def test_check_without_skip(self, mock_prereqs, mock_python_deps):
        """Test check() runs prerequisites when SKIP_PREREQUISITES_CHECK is not set."""
        with mock.patch.dict('os.environ', {}, clear=True):
            checkdependencies.check()

        mock_prereqs.assert_called_once()
        mock_python_deps.assert_called_once()

    @mock.patch('pythonforandroid.checkdependencies.check_python_dependencies')
    @mock.patch('pythonforandroid.checkdependencies.check_and_install_default_prerequisites')
    def test_check_with_skip_set_to_zero(self, mock_prereqs, mock_python_deps):
        """Test check() runs prerequisites when SKIP_PREREQUISITES_CHECK=0."""
        with mock.patch.dict('os.environ', {'SKIP_PREREQUISITES_CHECK': '0'}):
            checkdependencies.check()

        mock_prereqs.assert_called_once()
        mock_python_deps.assert_called_once()
