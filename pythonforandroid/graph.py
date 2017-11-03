
from copy import deepcopy
from itertools import product
from sys import exit

from pythonforandroid.logger import (info, warning, error)
from pythonforandroid.recipe import Recipe
from pythonforandroid.bootstrap import Bootstrap


class RecipeOrder(dict):

    def __init__(self, ctx):
        self.ctx = ctx

    def conflicts(self, name):
        for name in self.keys():
            try:
                recipe = Recipe.get_recipe(name, self.ctx)
                conflicts = recipe.conflicts
            except IOError:
                conflicts = []

            if any([c in self for c in conflicts]):
                return True
        return False


def recursively_collect_orders(name, ctx, orders=[]):
    '''For each possible recipe ordering, try to add the new recipe name
    to that order. Recursively do the same thing with all the
    dependencies of each recipe.

    '''
    try:
        recipe = Recipe.get_recipe(name, ctx)
        if recipe.depends is None:
            dependencies = []
        else:
            # make all dependencies into lists so that product will work
            dependencies = [([dependency] if not isinstance(
                dependency, (list, tuple))
                            else dependency) for dependency in recipe.depends]
        if recipe.conflicts is None:
            conflicts = []
        else:
            conflicts = recipe.conflicts
    except IOError:
        # The recipe does not exist, so we assume it can be installed
        # via pip with no extra dependencies
        dependencies = []
        conflicts = []

    new_orders = []
    # for each existing recipe order, see if we can add the new recipe name
    for order in orders:
        if name in order:
            new_orders.append(deepcopy(order))
            continue
        if order.conflicts(name):
            continue
        if any([conflict in order for conflict in conflicts]):
            continue

        for dependency_set in product(*dependencies):
            new_order = deepcopy(order)
            new_order[name] = set(dependency_set)

            dependency_new_orders = [new_order]
            for dependency in dependency_set:
                dependency_new_orders = recursively_collect_orders(
                    dependency, ctx, dependency_new_orders)

            new_orders.extend(dependency_new_orders)

    return new_orders


def find_order(graph):
    '''
    Do a topological sort on the dependency graph dict.
    '''
    while graph:
        # Find all items without a parent
        leftmost = [l for l, s in graph.items() if not s]
        if not leftmost:
            raise ValueError('Dependency cycle detected! %s' % graph)
        # If there is more than one, sort them for predictable order
        leftmost.sort()
        for result in leftmost:
            # Yield and remove them from the graph
            yield result
            graph.pop(result)
            for bset in graph.values():
                bset.discard(result)


def get_recipe_order_and_bootstrap(ctx, names, bs=None):
    recipes_to_load = set(names)
    if bs is not None and bs.recipe_depends:
        recipes_to_load = recipes_to_load.union(set(bs.recipe_depends))

    possible_orders = []

    # get all possible order graphs, as names may include tuples/lists
    # of alternative dependencies
    names = [([name] if not isinstance(name, (list, tuple)) else name)
             for name in names]
    for name_set in product(*names):
        new_possible_orders = [RecipeOrder(ctx)]
        for name in name_set:
            new_possible_orders = recursively_collect_orders(
                name, ctx, orders=new_possible_orders)
        possible_orders.extend(new_possible_orders)

    # turn each order graph into a linear list if possible
    orders = []
    for possible_order in possible_orders:
        try:
            order = find_order(possible_order)
        except ValueError:  # a circular dependency was found
            info('Circular dependency found in graph {}, skipping it.'.format(
                possible_order))
            continue
        except:
            warning('Failed to import recipe named {}; the recipe exists '
                    'but appears broken.'.format(name))
            warning('Exception was:')
            raise
        orders.append(list(order))

    # prefer python2 and SDL2 if available
    orders = sorted(orders,
                    key=lambda order: -('python2' in order) - ('sdl2' in order))

    if not orders:
        error('Didn\'t find any valid dependency graphs.')
        error('This means that some of your requirements pull in '
              'conflicting dependencies.')
        error('Exiting.')
        exit(1)
    # It would be better to check against possible orders other
    # than the first one, but in practice clashes will be rare,
    # and can be resolved by specifying more parameters
    chosen_order = orders[0]
    if len(orders) > 1:
        info('Found multiple valid dependency orders:')
        for order in orders:
            info('    {}'.format(order))
        info('Using the first of these: {}'.format(chosen_order))
    else:
        info('Found a single valid recipe set: {}'.format(chosen_order))

    if bs is None:
        bs = Bootstrap.get_bootstrap_from_recipes(chosen_order, ctx)
        recipes, python_modules, bs = get_recipe_order_and_bootstrap(
            ctx, chosen_order, bs=bs)
    else:
        # check if each requirement has a recipe
        recipes = []
        python_modules = []
        for name in chosen_order:
            try:
                recipe = Recipe.get_recipe(name, ctx)
                python_modules += recipe.python_depends
            except IOError:
                python_modules.append(name)
            else:
                recipes.append(name)

    python_modules = list(set(python_modules))
    return recipes, python_modules, bs
