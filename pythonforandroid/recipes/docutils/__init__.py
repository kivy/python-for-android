from pythonforandroid.toolchain import PythonRecipe

class DocutilsRecipe(PythonRecipe):

    url = ('http://prdownloads.sourceforge.net/docutils/'
           'docutils-{version}.tar.gz')
    # md5sum = '4622263b62c5c771c03502afa3157768'
    site_packages_name = 'docutils'
    depends = ['pil', ]  # 'lxml', ]

    version = '0.12'
    conflicts = []

recipe = DocutilsRecipe()
