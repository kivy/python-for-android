
from copy import deepcopy

from pythonforandroid.logger import (info, info_notify, warning)
from pythonforandroid.recipe import Recipe
from pythonforandroid.bootstrap import Bootstrap


class Graph(object):
    # Taken from the old python-for-android/depsort
    # Modified to include alternative dependencies
    def __init__(self):
        # `graph`: dict that maps each package to a set of its dependencies.
        self.graphs = [{}]
        # self.graph = {}

    def remove_redundant_graphs(self):
        '''Removes possible graphs if they are equivalent to others.'''
        graphs = self.graphs
        # Walk the list backwards so that popping elements doesn't
        # mess up indexing.

        # n.b. no need to test graph 0 as it will have been tested against
        # all others by the time we get to it
        for i in range(len(graphs) - 1, 0, -1):
            graph = graphs[i]

            # test graph i against all graphs 0 to i-1
            for j in range(0, i):
                comparison_graph = graphs[j]

                if set(comparison_graph.keys()) == set(graph.keys()):
                    # graph[i] == graph[j]
                    # so remove graph[i] and continue on to testing graph[i-1]
                    graphs.pop(i)
                    break

    def add(self, dependent, dependency):
        """Add a dependency relationship to the graph"""
        if isinstance(dependency, (tuple, list)):
            for graph in self.graphs[:]:
                for dep in dependency[1:]:
                    new_graph = deepcopy(graph)
                    self._add(new_graph, dependent, dep)
                    self.graphs.append(new_graph)
                self._add(graph, dependent, dependency[0])
        else:
            for graph in self.graphs:
                self._add(graph, dependent, dependency)
        self.remove_redundant_graphs()

    def _add(self, graph, dependent, dependency):
        '''Add a dependency relationship to a specific graph, where dependency
        must be a single dependency, not a list or tuple.
        '''
        graph.setdefault(dependent, set())
        graph.setdefault(dependency, set())
        if dependent != dependency:
            graph[dependent].add(dependency)

    def conflicts(self, conflict):
        graphs = self.graphs
        for i in range(len(graphs)):
            graph = graphs[len(graphs) - 1 - i]
            if conflict in graph:
                graphs.pop(len(graphs) - 1 - i)
        return len(graphs) == 0

    def remove_remaining_conflicts(self, ctx):
        # It's unpleasant to have to pass ctx as an argument...
        '''Checks all possible graphs for conflicts that have arisen during
        the additon of alternative repice branches, as these are not checked
        for conflicts at the time.'''
        new_graphs = []
        for i, graph in enumerate(self.graphs):
            for name in graph.keys():
                recipe = Recipe.get_recipe(name, ctx)
                if any([c in graph for c in recipe.conflicts]):
                    break
            else:
                new_graphs.append(graph)
        self.graphs = new_graphs

    def add_optional(self, dependent, dependency):
        """Add an optional (ordering only) dependency relationship to the graph

        Only call this after all mandatory requirements are added
        """
        for graph in self.graphs:
            if dependent in graph and dependency in graph:
                self._add(graph, dependent, dependency)

    def find_order(self, index=0):
        """Do a topological sort on a dependency graph

        :Parameters:
            :Returns:
                iterator, sorted items form first to last
        """
        graph = self.graphs[index]
        graph = dict((k, set(v)) for k, v in graph.items())
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
    '''Takes a list of recipe names and (optionally) a bootstrap. Then
    works out the dependency graph (including bootstrap recipes if
    necessary). Finally, if no bootstrap was initially selected,
    chooses one that supports all the recipes.
    '''
    graph = Graph()
    recipes_to_load = set(names)
    if bs is not None and bs.recipe_depends:
        info_notify('Bootstrap requires recipes {}'.format(bs.recipe_depends))
        recipes_to_load = recipes_to_load.union(set(bs.recipe_depends))
    recipes_to_load = list(recipes_to_load)
    recipe_loaded = []
    python_modules = []
    while recipes_to_load:
        name = recipes_to_load.pop(0)
        if name in recipe_loaded or isinstance(name, (list, tuple)):
            continue
        try:
            recipe = Recipe.get_recipe(name, ctx)
        except IOError:
            info('No recipe named {}; will attempt to install with pip'
                 .format(name))
            python_modules.append(name)
            continue
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            warning('Failed to import recipe named {}; the recipe exists '
                    'but appears broken.'.format(name))
            warning('Exception was:')
            raise
        graph.add(name, name)
        info('Loaded recipe {} (depends on {}{})'.format(
            name, recipe.depends,
            ', conflicts {}'.format(recipe.conflicts) if recipe.conflicts
            else ''))
        for depend in recipe.depends:
            graph.add(name, depend)
            recipes_to_load += recipe.depends
        for conflict in recipe.conflicts:
            if graph.conflicts(conflict):
                warning(
                    ('{} conflicts with {}, but both have been '
                     'included or pulled into the requirements.'
                     .format(recipe.name, conflict)))
                warning(
                    'Due to this conflict the build cannot continue, exiting.')
                exit(1)
        python_modules += recipe.python_depends
        recipe_loaded.append(name)
    graph.remove_remaining_conflicts(ctx)
    if len(graph.graphs) > 1:
        info('Found multiple valid recipe sets:')
        for g in graph.graphs:
            info('    {}'.format(g.keys()))
        info_notify('Using the first of these: {}'
                    .format(graph.graphs[0].keys()))
    elif len(graph.graphs) == 0:
        warning('Didn\'t find any valid dependency graphs, exiting.')
        exit(1)
    else:
        info('Found a single valid recipe set (this is good)')

    build_order = list(graph.find_order(0))
    if bs is None:  # It would be better to check against possible
                    # orders other than the first one, but in practice
                    # there will rarely be clashes, and the user can
                    # specify more parameters if necessary to resolve
                    # them.
        bs = Bootstrap.get_bootstrap_from_recipes(build_order, ctx)
        if bs is None:
            info('Could not find a bootstrap compatible with the '
                 'required recipes.')
            info('If you think such a combination should exist, try '
                 'specifying the bootstrap manually with --bootstrap.')
            exit(1)
        info('{} bootstrap appears compatible with the required recipes.'
             .format(bs.name))
        info('Checking this...')
        recipes_to_load = bs.recipe_depends
        # This code repeats the code from earlier! Should move to a function:
        while recipes_to_load:
            name = recipes_to_load.pop(0)
            if name in recipe_loaded or isinstance(name, (list, tuple)):
                continue
            try:
                recipe = Recipe.get_recipe(name, ctx)
            except ImportError:
                info('No recipe named {}; will attempt to install with pip'
                     .format(name))
                python_modules.append(name)
                continue
            graph.add(name, name)
            info('Loaded recipe {} (depends on {}{})'.format(
                name, recipe.depends,
                ', conflicts {}'.format(recipe.conflicts) if recipe.conflicts
                else ''))
            for depend in recipe.depends:
                graph.add(name, depend)
                recipes_to_load += recipe.depends
            for conflict in recipe.conflicts:
                if graph.conflicts(conflict):
                    warning(
                        ('{} conflicts with {}, but both have been '
                         'included or pulled into the requirements.'
                         .format(recipe.name, conflict)))
                    warning('Due to this conflict the build cannot continue, '
                            'exiting.')
                    exit(1)
            recipe_loaded.append(name)
        graph.remove_remaining_conflicts(ctx)
        build_order = list(graph.find_order(0))
    return build_order, python_modules, bs

    # Do a final check that the new bs doesn't pull in any conflicts
