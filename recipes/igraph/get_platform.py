from distutils.util import get_platform
from sys import version
print get_platform() + '-' + version[:3]
