from pythonforandroid.recipes.Pillow import PillowRecipe
from pythonforandroid.logger import warning


class PilRecipe(PillowRecipe):
    """A transparent wrapper around the Pillow recipe, it should build
    Pillow automatically as if "pillow" were specified in the
    requirements.
    """

    name = 'Pillow'  # ensures the Pillow recipe directory is used where necessary

    conflicts = ['pillow']

    def build_arch(self, arch):
        warning('PIL is no longer supported, building Pillow instead. '
                'This should be a drop-in replacement.')
        warning('It is recommended to change "pil" to "pillow" in your requirements, '
                'to ensure future compatibility')
        super().build_arch(arch)


recipe = PilRecipe()
