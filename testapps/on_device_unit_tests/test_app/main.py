import sys
if sys.version_info.major < 3:
    print(('Running under Python {} but these tests '
           'require Python 3+').format(sys.version_info.major))

import unittest

print('Imported unittest')

sys.path.append('./')
from tests import test_requirements
suite = unittest.TestLoader().loadTestsFromModule(test_requirements)
unittest.TextTestRunner().run(suite)

print('Ran tests')
