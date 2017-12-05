
from pythonforandroid.build import Context
from pythonforandroid.graph import get_recipe_order_and_bootstrap
from pythonforandroid.bootstrap import Bootstrap
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


@pytest.mark.parametrize('names,bootstrap', valid_combinations)
def test_valid_recipe_order_and_bootstrap(names, bootstrap):
    get_recipe_order_and_bootstrap(ctx, names, bootstrap)

invalid_combinations = [[['python2', 'python3crystax'], None],
                        [['python3'], Bootstrap.get_bootstrap('pygame', ctx)]]


@pytest.mark.parametrize('names,bootstrap', invalid_combinations)
def test_invalid_recipe_order_and_bootstrap(names, bootstrap):
    with pytest.raises(SystemExit):
        get_recipe_order_and_bootstrap(ctx, names, bootstrap)


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
