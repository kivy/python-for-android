print('Service Test App main.py was successfully called')

import sys
print('python version is: ', sys.version)
print('python sys.path is: ', sys.path)

from math import sqrt
print('import math worked')

for i in range(45, 50):
    print(i, sqrt(i))

print('Just printing stuff apparently worked, trying a simple service')

from jnius import autoclass
service = autoclass('org.test.testapp_service.ServiceTime')
mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
argument = 'test argument ok'
service.start(mActivity, argument)
