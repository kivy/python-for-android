print('main.py was successfully called')

import sys
print('python version is: ', sys.version)
print('python sys.path is: ', sys.path)

from math import sqrt
print('import math worked')

for i in range(45, 50):
    print(i, sqrt(i))

print('Just printing stuff apparently worked, trying a simple service')
import datetime, threading, time

next_call = time.time()


def service_timer():
    global next_call
    print('P4a datetime service: {}'.format(datetime.datetime.now()))
    next_call = next_call + 1
    threading.Timer(next_call - time.time(), service_timer).start()


print('Starting the service timer...')
service_timer()
