#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

from jnius import autoclass
from os import environ

DataBuilder = autoclass('androidx.work.Data$Builder')
P4a_test_workerWorker = autoclass('org.test.unit_tests_app.P4a_test_workerWorker')


def set_progress(progress):
    progress_data = DataBuilder().putInt('PROGRESS', progress).build()
    P4a_test_workerWorker.mWorker.setProgressAsync(progress_data)


argument = environ.get('PYTHON_SERVICE_ARGUMENT', '')
print(
    'app_worker.py was successfully called with argument: "{}"'.format(
        argument,
    ),
)

try:
    duration = int(argument)
except ValueError:
    duration = 60

print('Running the test worker for {} seconds'.format(duration))

remaining = duration
while remaining > 0:
    print(remaining, 'seconds remaining')

    progress = int((100.0 * (duration - remaining)) / duration)
    set_progress(progress)

    remaining -= 1
    time.sleep(1)
set_progress(100)

print('Exiting the test worker')
