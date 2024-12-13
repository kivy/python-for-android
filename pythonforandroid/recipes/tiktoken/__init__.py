from pythonforandroid.recipe import RustCompiledComponentsRecipe


class TiktokenRecipe(RustCompiledComponentsRecipe):
    name = 'tiktoken'
    version = '0.7.0'
    url = 'https://github.com/openai/tiktoken/archive/refs/tags/{version}.tar.gz'
    sha512sum = "bb2d8fd5acd660d60e690769e46cf29b06361343ea30e35613d27d55f44acf9834e51aef28f4ff316ef66f2130042079718cea04b2353301aef334cd7bd6d221"
    depends = ['regex', 'requests']


recipe = TiktokenRecipe()
