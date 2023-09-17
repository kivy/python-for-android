"""
    Helper functions for recipes.

    Recipes must supply a list of patches.

    Patches consist of a filename and an optional conditional, which is
    any function of the form:
        def patch_check(arch: string, recipe : Recipe) -> bool

    This library provides some helpful conditionals and mechanisms to
    join multiple conditionals.

    Example:
        patches = [
            ("linux_or_darwin_only.patch",
             check_any(is_linux, is_darwin),
            ("recent_android_API.patch",
             is_apt_gte(27)),
            ]
"""
from platform import uname
from packaging.version import Version


# Platform checks


def is_platform(platform):
    """
    Returns true if the host platform matches the parameter given.
    """

    def check(arch, recipe):
        return uname().system.lower() == platform.lower()

    return check


is_linux = is_platform("Linux")
is_darwin = is_platform("Darwin")
is_windows = is_platform("Windows")


def is_arch(xarch):
    """
    Returns true if the target architecture platform matches the parameter
    given.
    """

    def check(arch):
        return arch.arch == xarch

    return check


# Android API comparisons:
# Return true if the Android API level being targeted
# is equal (or >, >=, <, <= as appropriate) the given parameter


def is_api(apiver: int):
    def check(arch, recipe):
        return recipe.ctx.android_api == apiver

    return check


def is_api_gt(apiver: int):
    def check(arch, recipe):
        return recipe.ctx.android_api > apiver

    return check


def is_api_gte(apiver: int):
    def check(arch, recipe):
        return recipe.ctx.android_api >= apiver

    return check


def is_api_lt(apiver: int):
    def check(arch, recipe):
        return recipe.ctx.android_api < apiver

    return check


def is_api_lte(apiver: int):
    def check(arch, recipe):
        return recipe.ctx.android_api <= apiver

    return check


# Android API comparisons:


def is_ndk(ndk):
    """
    Return true if the Minimum Supported Android NDK level being targeted
    is equal the given parameter (which should be an AndroidNDK instance)
    """

    def check(arch, recipe):
        return recipe.ctx.ndk == ndk

    return check


# Recipe Version comparisons:
# These compare the Recipe's version with the provided string (or
# Packaging.Version).
#
# Warning: Both strings must conform to PEP 440 - e.g. "3.2.1" or "1.0rc1"


def is_version_gt(version):
    """Return true if the Recipe's version is greater"""

    def check(arch, recipe):
        return Version(recipe.version) > Version(version)

    return check


def is_version_lt(version):
    """Return true if the Recipe's version is less than"""

    def check(arch, recipe):
        return Version(recipe.version) < Version(version)

    return check


def version_starts_with(version_prefix):
    def check(arch, recipe):
        return recipe.version.startswith(version_prefix)

    return check


# Will Build


def will_build(recipe_name):
    """Return true if the recipe with this name is planned to be included in
    the distribution."""

    def check(arch, recipe):
        return recipe_name in recipe.ctx.recipe_build_order

    return check


# Conjunctions


def check_all(*patch_checks):
    """
    Given a collection of patch_checks as params, return if all returned true.
    """

    def check(arch, recipe):
        return all(patch_check(arch, recipe) for patch_check in patch_checks)

    return check


def check_any(*patch_checks):
    """
    Given a collection of patch_checks as params, return if any returned true.
    """

    def check(arch, recipe):
        return any(patch_check(arch, recipe) for patch_check in patch_checks)

    return check
