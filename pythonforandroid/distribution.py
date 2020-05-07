from os.path import exists, join
import glob
import json

from pythonforandroid.logger import (info, info_notify, warning, Err_Style, Err_Fore)
from pythonforandroid.util import current_directory, BuildInterruptingException
from shutil import rmtree


class Distribution:
    '''State container for information about a distribution (i.e. an
    Android project).

    This is separate from a Bootstrap because the Bootstrap is
    concerned with building and populating the dist directory, whereas
    the dist itself could also come from e.g. a binary download.
    '''
    ctx = None

    name = None  # A name identifying the dist. May not be None.
    needs_build = False  # Whether the dist needs compiling
    url = None
    dist_dir = None  # Where the dist dir ultimately is. Should not be None.
    ndk_api = None

    archs = []
    '''The names of the arch targets that the dist is built for.'''

    recipes = []

    description = ''  # A long description

    def __init__(self, ctx):
        self.ctx = ctx

    def __str__(self):
        return '<Distribution: name {} with recipes ({})>'.format(
            # self.name, ', '.join([recipe.name for recipe in self.recipes]))
            self.name, ', '.join(self.recipes))

    def __repr__(self):
        return str(self)

    @classmethod
    def get_distribution(
            cls,
            ctx,
            *,
            arch_name,  # required keyword argument: there is no sensible default
            name=None,
            recipes=[],
            ndk_api=None,
            force_build=False,
            extra_dist_dirs=[],
            require_perfect_match=False,
            allow_replace_dist=True
    ):
        '''Takes information about the distribution, and decides what kind of
        distribution it will be.

        If parameters conflict (e.g. a dist with that name already
        exists, but doesn't have the right set of recipes),
        an error is thrown.

        Parameters
        ----------
        name : str
            The name of the distribution. If a dist with this name already '
            exists, it will be used.
        ndk_api : int
            The NDK API to compile against, included in the dist because it cannot
            be changed later during APK packaging.
        arch_name : str
            The target architecture name to compile against, included in the dist because
            it cannot be changed later during APK packaging.
        recipes : list
            The recipes that the distribution must contain.
        force_download: bool
            If True, only downloaded dists are considered.
        force_build : bool
            If True, the dist is forced to be built locally.
        extra_dist_dirs : list
            Any extra directories in which to search for dists.
        require_perfect_match : bool
            If True, will only match distributions with precisely the
            correct set of recipes.
        allow_replace_dist : bool
            If True, will allow an existing dist with the specified
            name but incompatible requirements to be overwritten by
            a new one with the current requirements.
        '''

        possible_dists = Distribution.get_distributions(ctx)

        # Will hold dists that would be built in the same folder as an existing dist
        folder_match_dist = None

        # 0) Check if a dist with that name and architecture already exists
        if name is not None and name:
            possible_dists = [
                d for d in possible_dists if
                (d.name == name) and (arch_name in d.archs)]

            if possible_dists:
                # There should only be one folder with a given dist name *and* arch.
                # We could check that here, but for compatibility let's let it slide
                # and just record the details of one of them. We only use this data to
                # possibly fail the build later, so it doesn't really matter if there
                # was more than one clash.
                folder_match_dist = possible_dists[0]

        # 1) Check if any existing dists meet the requirements
        _possible_dists = []
        for dist in possible_dists:
            if (
                ndk_api is not None and dist.ndk_api != ndk_api
            ) or dist.ndk_api is None:
                continue
            for recipe in recipes:
                if recipe not in dist.recipes:
                    break
            else:
                _possible_dists.append(dist)
        possible_dists = _possible_dists

        if possible_dists:
            info('Of the existing distributions, the following meet '
                 'the given requirements:')
            pretty_log_dists(possible_dists)
        else:
            info('No existing dists meet the given requirements!')

        # If any dist has perfect recipes, arch and NDK API, return it
        for dist in possible_dists:
            if force_build:
                continue
            if ndk_api is not None and dist.ndk_api != ndk_api:
                continue
            if arch_name is not None and arch_name not in dist.archs:
                continue
            if (set(dist.recipes) == set(recipes) or
                (set(recipes).issubset(set(dist.recipes)) and
                 not require_perfect_match)):
                info_notify('{} has compatible recipes, using this one'
                            .format(dist.name))
                return dist

        # If there was a name match but we didn't already choose it,
        # then the existing dist is incompatible with the requested
        # configuration and the build cannot continue
        if folder_match_dist is not None and not allow_replace_dist:
            raise BuildInterruptingException(
                'Asked for dist with name {name} with recipes ({req_recipes}) and '
                'NDK API {req_ndk_api}, but a dist '
                'with this name already exists and has either incompatible recipes '
                '({dist_recipes}) or NDK API {dist_ndk_api}'.format(
                    name=name,
                    req_ndk_api=ndk_api,
                    dist_ndk_api=folder_match_dist.ndk_api,
                    req_recipes=', '.join(recipes),
                    dist_recipes=', '.join(folder_match_dist.recipes)))

        assert len(possible_dists) < 2

        # If we got this far, we need to build a new dist
        dist = Distribution(ctx)
        dist.needs_build = True

        if not name:
            filen = 'unnamed_dist_{}'
            i = 1
            while exists(join(ctx.dist_dir, filen.format(i))):
                i += 1
            name = filen.format(i)

        dist.name = name
        dist.dist_dir = join(
            ctx.dist_dir,
            generate_dist_folder_name(
                name,
                [arch_name] if arch_name is not None else None,
            )
        )
        dist.recipes = recipes
        dist.ndk_api = ctx.ndk_api
        dist.archs = [arch_name]

        return dist

    def folder_exists(self):
        return exists(self.dist_dir)

    def delete(self):
        rmtree(self.dist_dir)

    @classmethod
    def get_distributions(cls, ctx, extra_dist_dirs=[]):
        '''Returns all the distributions found locally.'''
        if extra_dist_dirs:
            raise BuildInterruptingException(
                'extra_dist_dirs argument to get_distributions '
                'is not yet implemented')
        dist_dir = ctx.dist_dir
        folders = glob.glob(join(dist_dir, '*'))
        for dir in extra_dist_dirs:
            folders.extend(glob.glob(join(dir, '*')))

        dists = []
        for folder in folders:
            if exists(join(folder, 'dist_info.json')):
                with open(join(folder, 'dist_info.json')) as fileh:
                    dist_info = json.load(fileh)
                dist = cls(ctx)
                dist.name = dist_info['dist_name']
                dist.dist_dir = folder
                dist.needs_build = False
                dist.recipes = dist_info['recipes']
                if 'archs' in dist_info:
                    dist.archs = dist_info['archs']
                if 'ndk_api' in dist_info:
                    dist.ndk_api = dist_info['ndk_api']
                else:
                    dist.ndk_api = None
                    warning(
                        "Distribution {distname}: ({distdir}) has been "
                        "built with an unknown api target, ignoring it, "
                        "you might want to delete it".format(
                            distname=dist.name,
                            distdir=dist.dist_dir
                        )
                    )
                dists.append(dist)
        return dists

    def save_info(self, dirn):
        '''
        Save information about the distribution in its dist_dir.
        '''
        with current_directory(dirn):
            info('Saving distribution info')
            with open('dist_info.json', 'w') as fileh:
                json.dump({'dist_name': self.name,
                           'bootstrap': self.ctx.bootstrap.name,
                           'archs': [arch.arch for arch in self.ctx.archs],
                           'ndk_api': self.ctx.ndk_api,
                           'use_setup_py': self.ctx.use_setup_py,
                           'recipes': self.ctx.recipe_build_order + self.ctx.python_modules,
                           'hostpython': self.ctx.hostpython,
                           'python_version': self.ctx.python_recipe.major_minor_version_string},
                          fileh)


def pretty_log_dists(dists, log_func=info):
    infos = []
    for dist in dists:
        ndk_api = 'unknown' if dist.ndk_api is None else dist.ndk_api
        infos.append('{Fore.GREEN}{Style.BRIGHT}{name}{Style.RESET_ALL}: min API {ndk_api}, '
                     'includes recipes ({Fore.GREEN}{recipes}'
                     '{Style.RESET_ALL}), built for archs ({Fore.BLUE}'
                     '{archs}{Style.RESET_ALL})'.format(
                         ndk_api=ndk_api,
                         name=dist.name, recipes=', '.join(dist.recipes),
                         archs=', '.join(dist.archs) if dist.archs else 'UNKNOWN',
                         Fore=Err_Fore, Style=Err_Style))

    for line in infos:
        log_func('\t' + line)


def generate_dist_folder_name(base_dist_name, arch_names=None):
    """Generate the distribution folder name to use, based on a
    combination of the input arguments.

    Parameters
    ----------
    base_dist_name : str
        The core distribution identifier string
    arch_names : list of str
        The architecture compile targets
    """
    if arch_names is None:
        arch_names = ["no_arch_specified"]

    return '{}__{}'.format(
        base_dist_name,
        '_'.join(arch_names)
    )
