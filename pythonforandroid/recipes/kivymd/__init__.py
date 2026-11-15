from pythonforandroid.recipe import PythonRecipe


class kivyMDRecipe(PythonRecipe):
    version = "365aa9b96eee63e0e29c04de297dd222f478fce5"
    url = "https://github.com/kivymd/KivyMD/archive/{version}.zip"

    depends = [
        "kivy",
        "materialyoucolor",
        "exceptiongroup",
        "asyncgui",
        "asynckivy",
    ]
    site_packages_name = "kivyMD"
    patches = ["kv.patch"]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True


recipe = kivyMDRecipe()
