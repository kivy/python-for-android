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
    set_device_orientation,
)


app = Flask(__name__)
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
    )


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


@app.route('/vibrate')
def vibrate():
    if not RUNNING_ON_ANDROID:
        print(NON_ANDROID_DEVICE_MSG, '...cancelled vibrate.')
        return NON_ANDROID_DEVICE_MSG

    args = request.args
    if 'time' not in args:
        print('ERROR: asked to vibrate but without time argument')
    print('asked to vibrate', args['time'])
    return vibrate_with_pyjnius(int(float(args['time']) * 1000))


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
    return set_device_orientation(direction)
