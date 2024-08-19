from pythonforandroid.recipe import RustCompiledComponentsRecipe


class TiktokenRecipe(RustCompiledComponentsRecipe):
    name = 'tiktoken'
    version = '0.7.0'
    url = 'https://github.com/openai/tiktoken/archive/refs/tags/{version}.tar.gz'
    depends = ['regex', 'requests']


recipe = TiktokenRecipe()
