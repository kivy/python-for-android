
from pythonforandroid.toolchain import PythonRecipe, shprint
import sh


class FlaskRecipe(PythonRecipe):
    version = '0.10.1'  # The webserver of 'master' seems to fail
                        # after a little while on Android, so use
                        # 0.10.1 at least for now
    url = 'https://github.com/pallets/flask/archive/{version}.zip'

    depends = [('python2', 'python3crystax'), 'setuptools', 'genericndkbuild']

    python_depends = ['jinja2', 'werkzeug', 'markupsafe', 'itsdangerous', 'click']

    call_hostpython_via_targetpython = False
    install_in_hostpython = False


recipe = FlaskRecipe()
