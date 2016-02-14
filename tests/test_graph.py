
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
combinations = list(product(name_sets, bootstraps))
combinations.extend(
    [(['python3'], Bootstrap.get_bootstrap('sdl2', ctx))])

@pytest.mark.parametrize('names,bootstrap', combinations)
def test_get_recipe_order_and_bootstrap(names, bootstrap):
    get_recipe_order_and_bootstrap(ctx, names, bootstrap)


if __name__ == "__main__":
    get_recipe_order_and_bootstrap(ctx, ['python2'], None)
