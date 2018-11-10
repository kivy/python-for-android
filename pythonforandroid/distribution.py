from os.path import exists, join
import glob
import json

from pythonforandroid.logger import (info, info_notify, warning,
                                     Err_Style, Err_Fore, error)
from pythonforandroid.util import current_directory


class Distribution(object):
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
    '''The arch targets that the dist is built for.'''

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
    def get_distribution(cls, ctx, name=None, recipes=[],
                         ndk_api=None,
                         force_build=False,
                         extra_dist_dirs=[],
                         require_perfect_match=False):
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
        '''

        existing_dists = Distribution.get_distributions(ctx)

        needs_build = True  # whether the dist needs building, will be returned

        possible_dists = existing_dists

        name_match_dist = None

        # 0) Check if a dist with that name already exists
        if name is not None and name:
            possible_dists = [d for d in possible_dists if d.name == name]
            if possible_dists:
                name_match_dist = possible_dists[0]

        # 1) Check if any existing dists meet the requirements
        _possible_dists = []
        for dist in possible_dists:
            if ndk_api is not None and dist.ndk_api != ndk_api:
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

        # If any dist has perfect recipes and ndk API, return it
        for dist in possible_dists:
            if force_build:
                continue
            if ndk_api is not None and dist.ndk_api != ndk_api:
                continue
            if (set(dist.recipes) == set(recipes) or
                (set(recipes).issubset(set(dist.recipes)) and
                 not require_perfect_match)):
                info_notify('{} has compatible recipes, using this one'
                            .format(dist.name))
                return dist

        assert len(possible_dists) < 2

        # If there was a name match but we didn't already choose it,
        # then the existing dist is incompatible with the requested
        # configuration and the build cannot continue
        if name_match_dist is not None:
            error('Asked for dist with name {name} with recipes ({req_recipes}) and '
                  'NDK API {req_ndk_api}, but a dist '
                  'with this name already exists and has either incompatible recipes '
                  '({dist_recipes}) or NDK API {dist_ndk_api}'.format(
                      name=name,
                      req_ndk_api=ndk_api,
                      dist_ndk_api=name_match_dist.ndk_api,
                      req_recipes=', '.join(recipes),
                      dist_recipes=', '.join(name_match_dist.recipes)))
            error('No compatible dist found, so exiting.')
            exit(1)

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
        dist.dist_dir = join(ctx.dist_dir, dist.name)
        dist.recipes = recipes
        dist.ndk_api = ctx.ndk_api

        return dist

    @classmethod
    def get_distributions(cls, ctx, extra_dist_dirs=[]):
        '''Returns all the distributions found locally.'''
        if extra_dist_dirs:
            warning('extra_dist_dirs argument to get_distributions '
                    'is not yet implemented')
            exit(1)
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
                dist.name = folder.split('/')[-1]
                dist.dist_dir = folder
                dist.needs_build = False
                dist.recipes = dist_info['recipes']
                if 'archs' in dist_info:
                    dist.archs = dist_info['archs']
                dist.ndk_api = dist_info['ndk_api']
                dists.append(dist)
        return dists

    def save_info(self, dirn):
        '''
        Save information about the distribution in its dist_dir.
        '''
        with current_directory(dirn):
            info('Saving distribution info')
            with open('dist_info.json', 'w') as fileh:
                json.dump({'dist_name': self.ctx.dist_name,
                           'bootstrap': self.ctx.bootstrap.name,
                           'archs': [arch.arch for arch in self.ctx.archs],
                           'ndk_api': self.ctx.ndk_api,
                           'recipes': self.ctx.recipe_build_order + self.ctx.python_modules},
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
