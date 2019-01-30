import sys
if sys.version_info.major < 3:
    print(('Running under Python {} but these tests '
           'require Python 3+').format(sys.version_info.major))

import unittest
import importlib

print('Imported unittest')


class PythonTestMixIn(object):

    module_import = None

    def test_import_module(self):
        """Test importing the specified Python module name. This import test
        is common to all Python modules, it does not test any further
        functionality.
        """
        self.assertIsNotNone(
            self.module_import,
            'module_import is not set (was default None)')

        importlib.import_module(self.module_import)

    def test_run_module(self):
        """Import the specified module and do something with it as a minimal
        check that it actually works.

        This test fails by default, it must be overridden by every
        child test class.
        """

        self.fail('This test must be overridden by {}'.format(self))

print('Defined test case')

import sys
sys.path.append('./')
from tests import test_requirements
suite = unittest.TestLoader().loadTestsFromModule(test_requirements)
unittest.TextTestRunner().run(suite)

print('Ran tests')
