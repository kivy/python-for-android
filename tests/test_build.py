import unittest
from unittest import mock

from pythonforandroid.build import run_pymodules_install


class TestBuildBasic(unittest.TestCase):

    def test_run_pymodules_install_optional_project_dir(self):
        """
        Makes sure the `run_pymodules_install()` doesn't crash when the
        `project_dir` optional parameter is None, refs #1898
        """
        ctx = mock.Mock()
        modules = []
        project_dir = None
        with mock.patch('pythonforandroid.build.info') as m_info:
            assert run_pymodules_install(ctx, modules, project_dir) is None
        assert m_info.call_args_list[-1] == mock.call(
            'No Python modules and no setup.py to process, skipping')
