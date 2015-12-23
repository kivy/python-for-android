from os import uname

class ComposableFunction(object):
    def __init__(self, function):
        self.func = function
        
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __and__(self, f):
        return ComposableFunction(lambda *args, **kwargs: self(*args, **kwargs) and f(*args, **kwargs))

    def __or__(self, f):
        return ComposableFunction(lambda *args, **kwargs: self(*args, **kwargs) or f(*args, **kwargs))


def check_all(*callables):
    def check(**kwargs):
        return all(c(**kwargs) for c in callables)
    return ComposableFunction(check)


def check_any(*callables):
    def check(**kwargs):
        return any(c(**kwargs) for c in callables)
    return ComposableFunction(check)


def is_platform(platform):
    def is_x(**kwargs):
        return uname()[0] == platform
    return ComposableFunction(is_x)

is_linux = is_platform('Linux')
is_darwin = is_platform('Darwin')


def is_arch(xarch):
    def is_x(arch, **kwargs):
        return arch.arch == xarch
    return ComposableFunction(is_x)


def is_api_gt(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api > apiver
    return ComposableFunction(is_x)


def is_api_gte(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api >= apiver
    return ComposableFunction(is_x)


def is_api_lt(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api < apiver
    return ComposableFunction(is_x)


def is_api_lte(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api <= apiver
    return ComposableFunction(is_x)


def is_api(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api == apiver
    return ComposableFunction(is_x)


def will_build(recipe_name):
    def will(recipe, **kwargs):
        return recipe_name in recipe.ctx.recipe_build_order
    return ComposableFunction(will)


def is_ndk(ndk):
    def is_x(recipe, **kwargs):
        return recipe.ctx.ndk == ndk
    return is_x

