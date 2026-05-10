from pythonforandroid.toolchain import Bootstrap


class ServiceOnlyBootstrap(Bootstrap):

    name = 'service_only'

    recipe_depends = list(
        set(Bootstrap.recipe_depends).union({'genericndkbuild'})
    )


bootstrap = ServiceOnlyBootstrap()
