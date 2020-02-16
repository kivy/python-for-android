from os import uname
from distutils.version import LooseVersion


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
        return uname()[0] == platform
    return is_x


is_linux = is_platform('Linux')
is_darwin = is_platform('Darwin')


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


def is_version_gt(version):
    def is_x(recipe, **kwargs):
        return LooseVersion(recipe.version) > version


def is_version_lt(version):
    def is_x(recipe, **kwargs):
        return LooseVersion(recipe.version) < version
    return is_x


def version_starts_with(version):
    def is_x(recipe, **kwargs):
        return recipe.version.startswith(version)
    return is_x
