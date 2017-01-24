import pythonforandroid.sh as sh


def check_all(*callables):
    def check(**kwargs):
        return all(c(**kwargs) for c in callables)
    return check


def check_any(*callables):
    def check(**kwargs):
        return any(c(**kwargs) for c in callables)
    return check


def is_platform(platform):
    def is_x(**kwargs):
        return sh.uname('-o').stdout.strip() == platform
    return is_x

is_linux = is_platform('Linux')
is_darwin = is_platform('Darwin')
is_msys = is_platform('Msys')


def is_arch(xarch):
    def is_x(arch, **kwargs):
        return arch.arch == xarch
    return is_x


def is_api_gt(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api > apiver
    return is_x


def is_api_gte(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api >= apiver
    return is_x


def is_api_lt(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api < apiver
    return is_x


def is_api_lte(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api <= apiver
    return is_x


def is_api(apiver):
    def is_x(recipe, **kwargs):
        return recipe.ctx.android_api == apiver
    return is_x


def will_build(recipe_name):
    def will(recipe, **kwargs):
        return recipe_name in recipe.ctx.recipe_build_order
    return will


def is_ndk(ndk):
    def is_x(recipe, **kwargs):
        return recipe.ctx.ndk == ndk
    return is_x

