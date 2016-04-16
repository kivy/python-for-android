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

@app.route('/')
def page1():
    return render_template('index.html')

@app.route('/page2')
def page2():
    return render_template('page2.html')

from os import curdir
from os.path import realpath
print('curdir', realpath(curdir))
if realpath(curdir).startswith('/data'):
    app.run(debug=False)
else:
    app.run(debug=True)
