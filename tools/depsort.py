#! /usr/bin/env python2

import argparse
import sys

class Graph(object):
    def __init__(self):
        # `graph`: dict that maps each package to a set of its dependencies.
        self.graph = {}

    def add(self, dependent, dependency):
        """Add a dependency relationship to the graph"""
        self.graph.setdefault(dependent, set())
        self.graph.setdefault(dependency, set())
        if dependent != dependency:
            self.graph[dependent].add(dependency)

    def add_optional(self, dependent, dependency):
        """Add an optional (ordering only) dependency relationship to the graph

        Only call this after all mandatory requirements are added
        """
        if dependent in self.graph and dependency in self.graph:
            self.add(dependent, dependency)

    def find_order(self):
        """Do a topological sort on a dependency graph

        :Parameters:
            :Returns:
                iterator, sorted items form first to last
        """
        graph = dict((k, set(v)) for k, v in self.graph.items())
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


def lines_to_relationships(lines):
    """Do a topological sort from a list of space-separated lines

    :Parameters:
        `lines`: Iterable of lines in the format
            "dependent dependency_0 dependency_1 ... dependency_n"

    :Returns:
        iterator of (dependent, dependency) tuples
    """
    for line in lines:
        line = line.split()
        if line:
            dependent = line[0]
            for dependency in line:
                yield dependent, dependency


def topo_sort_lines(lines, lines_optional=()):
    """Do a topological sort from a list of space-separated lines

    :Parameters:
        `lines`: Iterable of lines in the format
            "dependent dependency_0 dependency_1 ... dependency_n"

        `lines`: Iterable of lines with *optional* (ordering-only) dependencies
            "dependent dependency_0 dependency_1 ... dependency_n"

    :Returns:
        string, Sorted dependencies, space-separated
    """
    graph = Graph()
    for dependent, dependency in lines_to_relationships(lines):
        graph.add(dependent, dependency)
    for dependent, dependency in lines_to_relationships(lines_optional):
        graph.add_optional(dependent, dependency)
    return ' '.join(graph.find_order())


def test_depsort_1():
    lines = [
        'c a',
        'b c',
        'd b',
        'w z',
        'a w',
    ]
    assert topo_sort_lines(lines) == 'z w a c b d'


def test_depsort_2():
    lines = [
        'l k',
        'm l',
        'a k',
        'd a',
        'l d',
        's l',
        'm s',
    ]
    assert topo_sort_lines(lines) == 'k a d l s m'


def test_depsort_3():
    lines = [
        'z a',
        's z',
        'z z',
        's s',
    ]
    assert topo_sort_lines(lines) == 'a z s'


def test_depsort_4():
    lines = [
        'f d',
        'g f',
        'r f',
        't r',
        'y t',
        'g y',
    ]
    assert topo_sort_lines(lines) == 'd f r t y g'


def test_depsort_5():
    lines = [
        'a b c d e f',
        'e f',
        'g',
    ]
    assert topo_sort_lines(lines) == 'b c d f g e a'


def test_depsort_6():
    lines = [
        ' numpy python ',
        ' kivy pygame pyjnius android ',
        ' python hostpython ',
        ' pygame sdl ',
        ' android pygame ',
        ' pyjnius python ',
        ' sdl python ',
        ' hostpython ',
    ]
    assert topo_sort_lines(lines) == (
        'hostpython python numpy pyjnius sdl pygame android kivy')


def test_depsort_optional_1():
    lines = [' myapp openssl python ']
    optional = ['python openssl']
    assert topo_sort_lines(lines, optional) == 'openssl python myapp'


def test_depsort_optional_2():
    lines = [' myapp openssl python ']
    # Just for testing purposes, make openssl soft-depend on python
    optional = ['openssl python']
    assert topo_sort_lines(lines, optional) == 'python openssl myapp'


def test_depsort_optional_3():
    lines = ['myapp openssl']
    optional = ['python openssl']
    assert topo_sort_lines(lines, optional) == 'openssl myapp'


def test_depsort_optional_4():
    lines = ['myapp python']
    optional = ['python openssl']
    assert topo_sort_lines(lines, optional) == 'python myapp'


def test_depsort_optional_4():
    lines = ['myapp']
    optional = ['python openssl']
    assert topo_sort_lines(lines, optional) == 'myapp'


def main(argv):
    parser = argparse.ArgumentParser(
        description="Sort dependencies given on standard input")
    parser.add_argument('--optional', type=argparse.FileType('r'),
                        help='File with optional (ordering-only) dependencies')
    args = parser.parse_args(argv[1:])
    return topo_sort_lines(sys.stdin, lines_optional=args.optional or [])


if __name__ == '__main__':
    print main(sys.argv)
