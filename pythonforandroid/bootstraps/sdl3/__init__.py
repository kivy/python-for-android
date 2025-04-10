from pythonforandroid.bootstraps._sdl_common import SDLGradleBootstrap


class SDL3GradleBootstrap(SDLGradleBootstrap):
    name = "sdl3"

    recipe_depends = list(
        set(SDLGradleBootstrap.recipe_depends).union({"sdl3"})
    )


bootstrap = SDL3GradleBootstrap()
