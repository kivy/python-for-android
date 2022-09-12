print('main.py was successfully called')
print('this is the new main.py')

import sys
print('python version is: ' + sys.version)
print('python path is', sys.path)

import os
print('imported os')
print('contents of this dir', os.listdir('./'))

from flask import (
    Flask,
    current_app,
    jsonify,
    render_template,
    request,
    Markup
)

print('imported flask etc')

from constants import RUNNING_ON_ANDROID
from tools import (
    run_test_suites_into_buffer,
    get_failed_unittests_from,
    vibrate_with_pyjnius,
    get_android_python_activity,
    get_work_manager,
    set_device_orientation,
    skip_if_not_running_from_android_device,
)


class App(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_running = False
        self.work_request = None

    def get_status(self):
        return jsonify({
            'service_running': self.service_running,
            'worker_running': self.worker_running,
        })

    @property
    @skip_if_not_running_from_android_device
    def service(self):
        from jnius import autoclass

        return autoclass('org.test.unit_tests_app.ServiceP4a_test_service')

    @skip_if_not_running_from_android_device
    def service_start(self):
        activity = get_android_python_activity()
        self.service.start(activity, 'Some argument')
        self.service_running = True

    @skip_if_not_running_from_android_device
    def service_stop(self):
        activity = get_android_python_activity()
        self.service.stop(activity)
        self.service_running = False

    @property
    @skip_if_not_running_from_android_device
    def P4a_test_workerWorker(self):
        from jnius import autoclass

        return autoclass('org.test.unit_tests_app.P4a_test_workerWorker')

    @skip_if_not_running_from_android_device
    def worker_start(self):
        from jnius import autoclass

        if self.worker_running:
            return

        OneTimeWorkRequestBuilder = autoclass('androidx.work.OneTimeWorkRequest$Builder')
        data = self.P4a_test_workerWorker.buildInputData('10')
        self.work_request = (
            OneTimeWorkRequestBuilder(self.P4a_test_workerWorker._class)
            .setInputData(data)
            .build()
        )
        work_manager = get_work_manager()
        op = work_manager.enqueue(self.work_request)
        op.getResult().get()

    @skip_if_not_running_from_android_device
    def worker_stop(self):
        if self.worker_running:
            work_manager = get_work_manager()
            op = work_manager.cancelWorkById(self.work_request.getId())
            op.getResult().get()

    @property
    @skip_if_not_running_from_android_device
    def work_info(self):
        if self.work_request is None:
            return None

        work_manager = get_work_manager()
        return work_manager.getWorkInfoById(self.work_request.getId()).get()

    @property
    @skip_if_not_running_from_android_device
    def worker_running(self):
        info = self.work_info
        if info is None:
            print('Work request not started')
            return False
        state = info.getState()
        print('Work request state:', state.toString())
        return not state.isFinished()


app = App(__name__)
TESTS_TO_PERFORM = dict()
NON_ANDROID_DEVICE_MSG = 'Not running from Android device'


def get_html_for_tested_modules(tested_modules, failed_tests):
    modules_text = ''
    for n, module in enumerate(sorted(tested_modules)):
        print(module)
        base_text = '<label class="{color}">{module}</label>'
        if TESTS_TO_PERFORM[module] in failed_tests:
            color = 'text-red'
        else:
            color = 'text-green'
        if n != len(tested_modules) - 1:
            base_text += ', '

        modules_text += base_text.format(color=color, module=module)

    return Markup(modules_text)


@app.route('/')
def index():
    return render_template(
        'index.html',
        platform='Android' if RUNNING_ON_ANDROID else 'Desktop',
        service_running=current_app.service_running,
        worker_running=current_app.worker_running,
    )


@app.route('/status')
def status():
    return current_app.get_status()


@app.route('/unittests')
def unittests():
    import unittest
    print('Imported unittest')

    print("loading tests...")
    suites = unittest.TestLoader().loadTestsFromNames(
        list(TESTS_TO_PERFORM.values()),
    )

    print("running unittest...")
    terminal_output = run_test_suites_into_buffer(suites)

    print("unittest result is:")
    unittest_error_text = terminal_output.split('\n')
    print(terminal_output)

    # get a nice colored `html` output for our tested recipes
    failed_tests = get_failed_unittests_from(
        terminal_output, TESTS_TO_PERFORM.values(),
    )
    colored_tested_recipes = get_html_for_tested_modules(
        TESTS_TO_PERFORM.keys(), failed_tests,
    )

    return render_template(
        'unittests.html',
        tested_recipes=colored_tested_recipes,
        unittests_output=unittest_error_text,
        platform='Android' if RUNNING_ON_ANDROID else 'Desktop',
    )


@app.route('/page2')
def page2():
    return render_template(
        'page2.html',
        platform='Android' if RUNNING_ON_ANDROID else 'Desktop',
    )


@app.route('/loadUrl')
def loadUrl():
    if not RUNNING_ON_ANDROID:
        print(NON_ANDROID_DEVICE_MSG, '...cancelled loadUrl.')
        return NON_ANDROID_DEVICE_MSG
    args = request.args
    if 'url' not in args:
        print('ERROR: asked to open an url but without url argument')
    print('asked to open url', args['url'])
    activity = get_android_python_activity()
    activity.loadUrl(args['url'])
    return ('', 204)


@app.route('/vibrate')
def vibrate():
    if not RUNNING_ON_ANDROID:
        print(NON_ANDROID_DEVICE_MSG, '...cancelled vibrate.')
        return NON_ANDROID_DEVICE_MSG

    args = request.args
    if 'time' not in args:
        print('ERROR: asked to vibrate but without time argument')
    print('asked to vibrate', args['time'])
    vibrate_with_pyjnius(int(float(args['time']) * 1000))
    return ('', 204)


@app.route('/orientation')
def orientation():
    if not RUNNING_ON_ANDROID:
        print(NON_ANDROID_DEVICE_MSG, '...cancelled orientation.')
        return NON_ANDROID_DEVICE_MSG
    args = request.args
    if 'dir' not in args:
        print('ERROR: asked to orient but no dir specified')
        return 'No direction specified '
    direction = args['dir']
    set_device_orientation(direction)
    return ('', 204)


@app.route('/service')
def service():
    if not RUNNING_ON_ANDROID:
        print(NON_ANDROID_DEVICE_MSG, '...cancelled service.')
        return (NON_ANDROID_DEVICE_MSG, 400)
    args = request.args
    if 'action' not in args:
        print('ERROR: asked to manage service but no action specified')
        return ('No action specified', 400)

    action = args['action']
    if action == 'start':
        current_app.service_start()
    else:
        current_app.service_stop()
    return ('', 204)


@app.route('/worker')
def worker():
    if not RUNNING_ON_ANDROID:
        print(NON_ANDROID_DEVICE_MSG, '...cancelled worker.')
        return (NON_ANDROID_DEVICE_MSG, 400)
    args = request.args
    if 'action' not in args:
        print('ERROR: asked to manage worker but no action specified')
        return ('No action specified', 400)

    action = args['action']
    if action == 'start':
        current_app.worker_start()
    elif action == 'stop':
        current_app.worker_stop()
    else:
        return ('Invalid action "{}"'.format(action), 400)
    return ('', 204)
