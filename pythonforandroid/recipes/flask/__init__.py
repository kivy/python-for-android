from pythonforandroid.recipe import PyProjectRecipe


class FlaskRecipe(PyProjectRecipe):
    version = '3.1.1'
    url = 'https://github.com/pallets/flask/archive/{version}.zip'
    python_depends = ['jinja2', 'werkzeug', 'markupsafe', 'itsdangerous', 'click', 'blinker']


recipe = FlaskRecipe()
