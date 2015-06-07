
from math import sqrt

for i in range(50):
    print(i, sqrt(i))

print('Just printing stuff apparently worked, trying pyjnius')

import jnius

print('Importing jnius worked')

print('Trying to autoclass activity')

from jnius import autoclass

print('Imported autoclass')

NewPythonActivity = autoclass('net.inclem.android.NewPythonActivity')

print(':o the autoclass worked!')

