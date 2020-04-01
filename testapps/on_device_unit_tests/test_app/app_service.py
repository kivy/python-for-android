#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import threading
import time

from os import environ

argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
print(
    'app_service.py was successfully called with argument: "{}"'.format(
        argument,
    ),
)

next_call = time.time()
next_call_in = 5  # seconds


def service_timer():
    global next_call
    print('P4a test service: {}'.format(datetime.datetime.now()))

    next_call += next_call_in
    threading.Timer(next_call - time.time(), service_timer).start()


print('Starting the test service timer...')
service_timer()
