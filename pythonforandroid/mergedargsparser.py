"""
This provides a wrapper that allows multiple different ArgumentParser's
parse_args() function to return an argument object that will have an
attribute for ANY argument provided through ANY of all the parsers with
a value of None.

With this, we can avoid missing attribute errors if a code path was
called through a different initial toolchain command. These could also
be avoided through tons of hasattr()/getattr() calls, but that tends
to become unwieldy.
"""


class MergedArgsOverlay(object):
    def __init__(self, original_args, all_args_names_set):
        self._regular_args = original_args
        self._all_possible_args = all_args_names_set

    @property
    def __dict__(self):
        # Needed because argparse may for subparsers call our overridden
        # parse_known_arguments() internally, then try to use vars()
        # on this and return a new repackaged Namespace() based on it.
        #
        # In this case we just want to return the original objects args,
        # since the "outside" parse_args/parse_known_args call will re-wrap
        # this anyway, and otherwise we'd just confuse argparse internals
        # with our additional None'd arguments.
        return dict(vars(self._regular_args))

    def __getattr__(self, name):
        if not name.startswith("__") and hasattr(self._regular_args, name):
            return getattr(self._regular_args, name)
        if name in self._all_possible_args:
            return None
        raise AttributeError("no such attribute {}".format(name))


def wrap_as_parser_with_merged_args(args_store_set, parser):
    original_parse_args = parser.parse_args
    original_parse_known_args = parser.parse_known_args
    original_add_argument = parser.add_argument

    def parse_args_override(*args):
        args_obj = original_parse_args(args)
        while isinstance(args_obj, MergedArgsOverlay):  # handle nested wraps
            args_obj = MergedArgsOverlay._regular_args
        return MergedArgsOverlay(args_obj, args_store_set)

    def parse_known_args_override(*args):
        args_obj, args_unknown = original_parse_known_args(*args)
        while isinstance(args_obj, MergedArgsOverlay):  # handle nested wraps
            args_obj = MergedArgsOverlay._regular_args
        return (MergedArgsOverlay(args_obj, args_store_set), args_unknown)

    def add_argument_override(*args, **kwargs):
        for arg in args:
            while arg.startswith("-"):
                arg = arg[1:]
            args_store_set.add(arg.replace("-", "_"))
        return original_add_argument(*args, **kwargs)

    parser.parse_args = parse_args_override
    parser.parse_known_args = parse_known_args_override
    parser.add_argument = add_argument_override
    return parser
