from pythonforandroid.build import Context
from pythonforandroid.graph import (
    fix_deplist, get_dependency_tuple_list_for_recipe,
    get_recipe_order_and_bootstrap, obvious_conflict_checker,
)
from pythonforandroid.bootstrap import Bootstrap
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import BuildInterruptingException
from itertools import product

from unittest import mock
import pytest

ctx = Context()

name_sets = [['python3'],
             ['kivy']]
bootstraps = [None,
              Bootstrap.get_bootstrap('sdl2', ctx)]
valid_combinations = list(product(name_sets, bootstraps))
valid_combinations.extend(
    [(['python3'], Bootstrap.get_bootstrap('sdl2', ctx)),
     (['kivy', 'python3'], Bootstrap.get_bootstrap('sdl2', ctx)),
     (['flask'], Bootstrap.get_bootstrap('webview', ctx)),
     (['pysdl2'], None),  # auto-detect bootstrap! important corner case
    ]
)
invalid_combinations = [
    [['pil', 'pillow'], None],
    [['pysdl2', 'genericndkbuild'], None],
]
invalid_combinations_simple = list(invalid_combinations)
# NOTE !! keep in mind when setting invalid_combinations_simple:
#
# This is used to test obvious_conflict_checker(), which only
# catches CERTAIN conflicts:
#
# This must be a list of conflicts where the conflict is ONLY in
# non-tuple/non-ambiguous dependencies, e.g.:
#
#     dependencies_1st = ["python2", "pillow"]
#     dependencies_2nd = ["python3", "pillow"]
#
# This however won't work:
#
#     dependencies_1st = [("python2", "python3"), "pillow"]
#
# (This is simply because the conflict checker doesn't resolve this to
# keep the code ismple enough)


def get_fake_recipe(name, depends=None, conflicts=None):
    recipe = mock.Mock()
    recipe.name = name
    recipe.get_opt_depends_in_list = lambda: []
    recipe.get_dir_name = lambda: name
    recipe.depends = list(depends or [])
    recipe.conflicts = list(conflicts or [])
    return recipe


def register_fake_recipes_for_test(monkeypatch, recipe_list):
    _orig_get_recipe = Recipe.get_recipe

    def mock_get_recipe(name, ctx):
        for recipe in recipe_list:
            if recipe.name == name:
                return recipe
        return _orig_get_recipe(name, ctx)
    # Note: staticmethod() needed for python ONLY, don't ask me why:
    monkeypatch.setattr(Recipe, 'get_recipe', staticmethod(mock_get_recipe))


@pytest.mark.parametrize('names,bootstrap', valid_combinations)
def test_valid_recipe_order_and_bootstrap(names, bootstrap):
    get_recipe_order_and_bootstrap(ctx, names, bootstrap)


@pytest.mark.parametrize('names,bootstrap', invalid_combinations)
def test_invalid_recipe_order_and_bootstrap(names, bootstrap):
    with pytest.raises(BuildInterruptingException) as e_info:
        get_recipe_order_and_bootstrap(ctx, names, bootstrap)
    assert "conflict" in e_info.value.message.lower()


def test_blacklist():
    # First, get order without blacklist:
    build_order, python_modules, bs = get_recipe_order_and_bootstrap(
        ctx, ["python3", "kivy"], None
    )
    # Now, obtain again with blacklist:
    build_order_2, python_modules_2, bs_2 = get_recipe_order_and_bootstrap(
        ctx, ["python3", "kivy"], None, blacklist=["libffi"]
    )
    assert "libffi" not in build_order_2
    assert set(build_order_2).union({"libffi"}) == set(build_order)

    # Check that we get a conflict when using webview and kivy combined:
    wbootstrap = Bootstrap.get_bootstrap('webview', ctx)
    with pytest.raises(BuildInterruptingException) as e_info:
        get_recipe_order_and_bootstrap(ctx, ["flask", "kivy"], wbootstrap)
    assert "conflict" in e_info.value.message.lower()

    # We should no longer get a conflict blacklisting sdl2:
    get_recipe_order_and_bootstrap(
        ctx, ["flask", "kivy"], wbootstrap, blacklist=["sdl2"]
    )


def test_get_dependency_tuple_list_for_recipe(monkeypatch):
    r = get_fake_recipe("recipe1", depends=[
        "libffi",
        ("libffi", "Pillow")
    ])
    dep_list = get_dependency_tuple_list_for_recipe(
        r, blacklist={"libffi"}
    )
    assert dep_list == [("pillow",)]


@pytest.mark.parametrize('names,bootstrap', valid_combinations)
def test_valid_obvious_conflict_checker(names, bootstrap):
    # Note: obvious_conflict_checker is stricter on input
    # (needs fix_deplist) than get_recipe_order_and_bootstrap!
    obvious_conflict_checker(ctx, fix_deplist(names))


@pytest.mark.parametrize('names,bootstrap',
                         invalid_combinations_simple  # see above for why this
                        )                             # is a separate list
def test_invalid_obvious_conflict_checker(names, bootstrap):
    # Note: obvious_conflict_checker is stricter on input
    # (needs fix_deplist) than get_recipe_order_and_bootstrap!
    with pytest.raises(BuildInterruptingException) as e_info:
        obvious_conflict_checker(ctx, fix_deplist(names))
    assert "conflict" in e_info.value.message.lower()


def test_misc_obvious_conflict_checker(monkeypatch):
    # Check that the assert about wrong input data is hit:
    with pytest.raises(AssertionError) as e_info:
        obvious_conflict_checker(
            ctx,
            ["this_is_invalid"]
            # (invalid because it isn't properly nested as tuple)
        )

    # Test that non-recipe dependencies work in overall:
    obvious_conflict_checker(
        ctx, fix_deplist(["python3", "notarecipelibrary"])
    )

    # Test that a conflict with a non-recipe dependency works:
    # This is currently not used, so we need a custom test recipe:
    # To get that, we simply modify one!
    with monkeypatch.context() as m:
        register_fake_recipes_for_test(m, [
            get_fake_recipe("recipe1", conflicts=[("fakelib")]),
        ])
        with pytest.raises(BuildInterruptingException) as e_info:
            obvious_conflict_checker(ctx, fix_deplist(["recipe1", "fakelib"]))
        assert "conflict" in e_info.value.message.lower()

    # Test a case where a recipe pulls in a conditional tuple
    # of additional dependencies. This is e.g. done for ('python3',
    # 'python2', ...) but most recipes don't depend on this anymore,
    # so we need to add a manual test for this case:
    with monkeypatch.context() as m:
        register_fake_recipes_for_test(m, [
            get_fake_recipe("recipe1", depends=[("libffi", "Pillow")]),
        ])
        obvious_conflict_checker(ctx, fix_deplist(["recipe1"]))


def test_indirectconflict_obvious_conflict_checker(monkeypatch):
    # Test a case where there's an indirect conflict, which also
    # makes sure the error message correctly blames the OUTER recipes
    # as original conflict source:
    with monkeypatch.context() as m:
        register_fake_recipes_for_test(m, [
            get_fake_recipe("outerrecipe1", depends=["innerrecipe1"]),
            get_fake_recipe("outerrecipe2", depends=["innerrecipe2"]),
            get_fake_recipe("innerrecipe1"),
            get_fake_recipe("innerrecipe2", conflicts=["innerrecipe1"]),
        ])
        with pytest.raises(BuildInterruptingException) as e_info:
            obvious_conflict_checker(
                ctx,
                fix_deplist(["outerrecipe1", "outerrecipe2"])
            )
        assert ("conflict" in e_info.value.message.lower() and
                "outerrecipe1" in e_info.value.message.lower() and
                "outerrecipe2" in e_info.value.message.lower())


def test_multichoice_obvious_conflict_checker(monkeypatch):
    # Test a case where there's a conflict with a multi-choice tuple:
    with monkeypatch.context() as m:
        register_fake_recipes_for_test(m, [
            get_fake_recipe("recipe1", conflicts=["lib1", "lib2"]),
            get_fake_recipe("recipe2", depends=[("lib1", "lib2")]),
        ])
        with pytest.raises(BuildInterruptingException) as e_info:
            obvious_conflict_checker(
                ctx,
                fix_deplist([("lib1", "lib2"), "recipe1"])
            )
        assert "conflict" in e_info.value.message.lower()


def test_bootstrap_dependency_addition():
    build_order, python_modules, bs = get_recipe_order_and_bootstrap(
        ctx, ['kivy'], None)
    assert ('hostpython3' in build_order)


def test_graph_deplist_transformation():
    test_pairs = [
        (["Pillow", ('python2', 'python3')],
         [('pillow',), ('python2', 'python3')]),
        (["Pillow", ('python2',)],
         [('pillow',), ('python2',)]),
    ]
    for (before_list, after_list) in test_pairs:
        assert fix_deplist(before_list) == after_list


def test_bootstrap_dependency_addition2():
    build_order, python_modules, bs = get_recipe_order_and_bootstrap(
        ctx, ['kivy', 'python3'], None)
    assert 'hostpython3' in build_order


if __name__ == "__main__":
    get_recipe_order_and_bootstrap(ctx, ['python3'],
                                   Bootstrap.get_bootstrap('sdl2', ctx))
