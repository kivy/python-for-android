from pythonforandroid.recipe import Recipe


class OpenCVExtrasRecipe(Recipe):
    """
    OpenCV extras recipe allows us to build extra modules from the
    `opencv_contrib` repository. It depends on opencv recipe and all the build
    of the modules will be performed inside opencv recipe build directory.

    .. note:: the version of this recipe should be the same than opencv recipe.

    .. warning:: Be aware that these modules are experimental, some of them
        maybe included in opencv future releases and removed from extras.

    .. seealso:: https://github.com/opencv/opencv_contrib

    """
    version = '4.0.1'
    url = 'https://github.com/opencv/opencv_contrib/archive/{version}.zip'
    depends = ['opencv']


recipe = OpenCVExtrasRecipe()
