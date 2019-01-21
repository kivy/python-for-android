import datetime
import threading
import time
from os import environ
argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
print('p4atime.py was successfully called with argument: "{}"'.format(argument))

next_call = time.time()


def service_timer():
    global next_call
    print('P4a datetime service: {}'.format(datetime.datetime.now()))
    next_call = next_call + 1
    threading.Timer(next_call - time.time(), service_timer).start()


print('Starting the service timer...')
service_timer()
