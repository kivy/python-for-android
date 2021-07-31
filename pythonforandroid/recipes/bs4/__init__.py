from pythonforandroid.recipe import PythonRecipe


class BeautifulSoup4(PythonRecipe):
    """ BeautifulSoup4 recipe """

    name = 'bs4'
    version = '4.9.3'
    depends = ["setuptools"]
    call_hostpython_via_targetpython = False
    install_in_hostpython = True

    @property
    def url(self):
        major_minor_index = self.version.find('.', 2)
        major_minor_version = self.version[:major_minor_index]

        return (
            'https://www.crummy.com/software/BeautifulSoup/bs4/download/'
            f'{major_minor_version}/beautifulsoup4-{self.version}.tar.gz'
        )


recipe = BeautifulSoup4()
