from pythonforandroid.recipe import PythonRecipe


class GeventWebsocketRecipe(PythonRecipe):
    version = '0.9.5'
    url = 'https://pypi.python.org/packages/source/g/gevent-websocket/gevent-websocket-{version}.tar.gz'
    depends = ['setuptools']
    site_packages_name = 'geventwebsocket'
    call_hostpython_via_targetpython = False


recipe = GeventWebsocketRecipe()
