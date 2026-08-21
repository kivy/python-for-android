from pythonforandroid.recipe import PyProjectRecipe


class FlaskRecipe(PyProjectRecipe):
    version = '3.1.1'
    url = 'https://github.com/pallets/flask/archive/{version}.zip'
    depends = ["markupsafe"]
    python_depends = ['jinja2', 'werkzeug', 'itsdangerous', 'click', 'blinker']


recipe = FlaskRecipe()
