print('main.py was successfully called')
print('this is the new main.py')

import os
print('imported os')

try:
    print('contents of ./lib/python2.7/site-packages/ etc.')
    print(os.listdir('./lib'))
    print(os.listdir('./lib/python2.7'))
    print(os.listdir('./lib/python2.7/site-packages'))
except OSError:
    print('could not look in dirs')
    print('this is expected on desktop')

import flask
print('flask1???')

print('contents of this dir', os.listdir('./'))

import flask
print('flask???')

import sys
print('pythonpath is', sys.path)


from flask import Flask
app = Flask(__name__)

from flask import (Flask, url_for, render_template, request, redirect,
                   flash)

print('imported flask etc')
print('importing pyjnius')

from jnius import autoclass
Context = autoclass('android.content.Context')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
activity = PythonActivity.mActivity

vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)

ActivityInfo = autoclass('android.content.pm.ActivityInfo')

@app.route('/')
def page1():
    return render_template('index.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

@app.route('/vibrate')
def vibrate():
    args = request.args
    if 'time' not in args:
        print('ERROR: asked to vibrate but without time argument')
    print('asked to vibrate', args['time'])

    vibrator.vibrate(float(args['time']) * 1000)
    print('vibrated')

@app.route('/loadUrl')
def loadUrl():
    args = request.args
    if 'url' not in args:
        print('ERROR: asked to open an url but without url argument')
    print('asked to open url', args['url'])
    activity.loadUrl(args['url'])

@app.route('/orientation')
def orientation():
    args = request.args
    if 'dir' not in args:
        print('ERROR: asked to orient but no dir specified')
    direction = args['dir']
    if direction not in ('horizontal', 'vertical'):
        print('ERROR: asked to orient to neither horizontal nor vertical')

    if direction == 'horizontal':
        activity.setRequestedOrientation(
            ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE)
    else:
        activity.setRequestedOrientation(
            ActivityInfo.SCREEN_ORIENTATION_PORTRAIT)


from os import curdir
from os.path import realpath
print('curdir', realpath(curdir))
if realpath(curdir).startswith('/data'):
    app.run(debug=False)
else:
    app.run(debug=True)
