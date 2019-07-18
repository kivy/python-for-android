from os.path import exists, join
import glob
import json

from pythonforandroid import __version__
from pythonforandroid.logger import (info, info_notify, warning, Err_Style, Err_Fore)
from pythonforandroid.util import current_directory, BuildInterruptingException
from shutil import rmtree


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
    android_api = None
    p4a_version = None

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
                         force_build=False,
                         extra_dist_dirs=[],
                         require_perfect_match=False,
                         allow_replace_dist=True):
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
        allow_replace_dist : bool
            If True, will allow an existing dist with the specified
            name but incompatible requirements to be overwritten by
            a new one with the current requirements.
        '''

        existing_dists = Distribution.get_distributions(ctx)

        possible_dists = existing_dists

        name_match_dist = None

        req_archs = [arch.arch for arch in ctx.archs]

        # 0) Check if a dist with that name already exists
        if name is not None and name:
            possible_dists = [d for d in possible_dists if d.name == name]
            if possible_dists:
                name_match_dist = possible_dists[0]

        # 1) Check if any existing dists meet the requirements
        _possible_dists = []
        for dist in possible_dists:
            if any(
                [
                    dist.ndk_api != ctx.ndk_api,
                    dist.android_api != ctx.android_api,
                    set(dist.archs) != set(req_archs),
                    dist.ndk_api is None,
                ]
            ):
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

        # 2) Of the possible dists we will select the one which contains the
        # requested recipes, unless we used the kwarg `force_build`
        for dist in possible_dists:
            if force_build:
                continue
            if (set(dist.recipes) == set(recipes) or
                (set(recipes).issubset(set(dist.recipes)) and
                 not require_perfect_match)):
                info_notify('{} has compatible recipes, using this one'
                            .format(dist.name))
                return dist

        assert len(possible_dists) < 2

        # 3) If there was a name match but we didn't already choose it,
        # then the existing dist is incompatible with the requested
        # configuration and the build cannot continue
        if name_match_dist is not None and not allow_replace_dist:
            raise BuildInterruptingException(
                '\n\tAsked for dist with name {name} and:'
                '\n\t-> recipes: ({req_recipes})'
                '\n\t-> NDK api: ({req_ndk_api})'
                '\n\t-> android api ({req_android_api})'
                '\n\t-> archs ({req_archs})'
                '\n...but a dist with this name already exists and has either '
                'incompatible:'
                '\n\t-> recipes: ({dist_recipes})'
                '\n\t-> NDK api: ({dist_ndk_api})'
                '\n\t-> android api ({dist_android_api})'
                '\n\t-> archs ({dist_archs})'.format(
                    name=name,
                    req_recipes=', '.join(recipes),
                    req_ndk_api=ctx.ndk_api,
                    req_android_api=ctx.android_api,
                    req_archs=', '.join(req_archs),
                    dist_recipes=', '.join(name_match_dist.recipes),
                    dist_ndk_api=name_match_dist.ndk_api,
                    dist_android_api=name_match_dist.android_api,
                    dist_archs=', '.join(name_match_dist.archs),
                )
            )

        # 4) If we got this far, we need to build a new dist
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
        dist.archs = req_archs
        dist.ndk_api = ctx.ndk_api
        dist.android_api = ctx.android_api

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
                dist.name = folder.split('/')[-1]
                dist.dist_dir = folder
                dist.needs_build = False
                dist.recipes = dist_info['recipes']
                for entry in {'archs', 'ndk_api', 'android_api'}:
                    setattr(dist, entry, dist_info.get(entry, None))
                    if entry not in dist_info:
                        warning(
                            "Distribution {distname}: ({distdir}) has been "
                            "built with an unknown {entry}, ignoring it, "
                            "you might want to delete it".format(
                                distname=dist.name,
                                distdir=dist.dist_dir,
                                entry=entry,
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
                json.dump({'dist_name': self.ctx.dist_name,
                           'bootstrap': self.ctx.bootstrap.name,
                           'archs': [arch.arch for arch in self.ctx.archs],
                           'ndk_api': self.ctx.ndk_api,
                           'android_api': self.ctx.android_api,
                           'use_setup_py': self.ctx.use_setup_py,
                           'recipes': self.ctx.recipe_build_order + self.ctx.python_modules,
                           'hostpython': self.ctx.hostpython,
                           'python_version': self.ctx.python_recipe.major_minor_version_string,
                           'p4a_version': __version__},
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
