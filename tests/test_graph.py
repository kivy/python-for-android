from pythonforandroid.build import Context
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.bootstrap import Bootstrap
from pythonforandroid.util import BuildInterruptingException
from itertools import product

import pytest


ctx = Context()

name_sets = [['python2'],
             ['kivy']]
bootstraps = [None,
              Bootstrap.get_bootstrap('pygame', ctx),
              Bootstrap.get_bootstrap('sdl2', ctx)]
valid_combinations = list(product(name_sets, bootstraps))
valid_combinations.extend(
    [(['python3crystax'], Bootstrap.get_bootstrap('sdl2', ctx)),
     (['kivy', 'python3crystax'], Bootstrap.get_bootstrap('sdl2', ctx))])
invalid_combinations = [[['python2', 'python3crystax'], None]]


@pytest.mark.parametrize('names,bootstrap', valid_combinations)
def test_valid_recipe_order_and_bootstrap(names, bootstrap):
    get_recipe_order_and_bootstrap(ctx, names, bootstrap)


@pytest.mark.parametrize('names,bootstrap', invalid_combinations)
def test_invalid_recipe_order_and_bootstrap(names, bootstrap):
    with pytest.raises(BuildInterruptingException) as e_info:
        get_recipe_order_and_bootstrap(ctx, names, bootstrap)
    assert e_info.value.message == (
        "Didn't find any valid dependency graphs. "
        "This means that some of your requirements pull in conflicting dependencies."
    )


def test_bootstrap_dependency_addition():
    build_order, python_modules, bs = get_recipe_order_and_bootstrap(
        ctx, ['kivy'], None)
    assert (('hostpython2' in build_order) or ('hostpython3' in build_order))


def test_bootstrap_dependency_addition2():
    build_order, python_modules, bs = get_recipe_order_and_bootstrap(
        ctx, ['kivy', 'python2'], None)
    assert 'hostpython2' in build_order


if __name__ == "__main__":
    get_recipe_order_and_bootstrap(ctx, ['python3'],
                                   Bootstrap.get_bootstrap('sdl2', ctx))
