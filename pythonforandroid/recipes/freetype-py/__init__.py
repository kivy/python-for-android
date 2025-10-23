from pythonforandroid.recipe import PyProjectRecipe


class FreetypePyRecipe(PyProjectRecipe):
    version = '2.5.1'
    url = ('https://files.pythonhosted.org/packages/d0/9c/'
           '61ba17f846b922c2d6d101cc886b0e8fb597c109cedfcb39b8c5d2304b54/'
           'freetype-py-{version}.zip')
    depends = ['freetype']
    site_packages_name = 'freetype'


recipe = FreetypePyRecipe()
