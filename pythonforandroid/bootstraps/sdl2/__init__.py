from pythonforandroid.bootstraps._sdl_common import SDLGradleBootstrap


class SDL2GradleBootstrap(SDLGradleBootstrap):
    name = "sdl2"

    recipe_depends = list(
        set(SDLGradleBootstrap.recipe_depends).union({"sdl2"})
    )


bootstrap = SDL2GradleBootstrap()
