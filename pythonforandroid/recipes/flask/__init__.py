
from pythonforandroid.recipe import PythonRecipe


class FlaskRecipe(PythonRecipe):
    # The webserver of 'master' seems to fail
    # after a little while on Android, so use
    # 0.10.1 at least for now
    version = '0.10.1'
    url = 'https://github.com/pallets/flask/archive/{version}.zip'

    depends = ['setuptools']

    python_depends = ['jinja2', 'werkzeug', 'markupsafe', 'itsdangerous', 'click']

    call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = FlaskRecipe()
