
from pythonforandroid.toolchain import PythonRecipe, shprint
import sh


class FlaskRecipe(PythonRecipe):
    version = 'master'
    url = 'https://github.com/pallets/flask/archive/{version}.zip'

    depends = [('python2', 'python3'), 'setuptools']

    python_depends = ['jinja2', 'werkzeug', 'markupsafe', 'itsdangerous', 'click']

    call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = FlaskRecipe()
