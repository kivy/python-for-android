
from math import sqrt
print('import math worked')

import sys

print('sys.path is', sys.path)

for i in range(45, 50):
    print(i, sqrt(i))

print('trying to import six')
try:
    import six
except ImportError:
    print('import failed')


print('trying to import six again')
try:
    import six
except ImportError:
    print('import failed (again?)')
print('import six worked!')

print('Just printing stuff apparently worked, trying pyjnius')

import jnius

print('Importing jnius worked')

print('trying to import stuff')

try:
    from jnius import cast
except ImportError:
    print('cast failed')

try:
    from jnius import ensureclass
except ImportError:
    print('ensureclass failed')

try:
    from jnius import JavaClass
except ImportError:
    print('JavaClass failed')

try:
    from jnius import jnius
except ImportError:
    print('jnius failed')

try:
    from jnius import reflect
except ImportError:
    print('reflect failed')

try:
    from jnius import find_javaclass
except ImportError:
    print('find_javaclass failed')

print('Trying to autoclass activity')

from jnius import autoclass

print('Imported autoclass')

PythonActivity = autoclass('org.kivy.android.PythonActivity')

print(':o the autoclass worked!')

