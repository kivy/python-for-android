from pythonforandroid.toolchain import Bootstrap


class WebViewBootstrap(Bootstrap):
    name = 'webview'

    recipe_depends = list(
        set(Bootstrap.recipe_depends).union({'genericndkbuild'})
    )


bootstrap = WebViewBootstrap()
