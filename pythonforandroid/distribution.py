from os.path import exists, join
import glob
import json

from pythonforandroid.logger import (info, info_notify, warning,
                                     Err_Style, Err_Fore)
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

        # 0) Check if a dist with that name already exists
        if name is not None and name:
            possible_dists = [d for d in possible_dists if d.name == name]

        # 1) Check if any existing dists meet the requirements
        _possible_dists = []
        for dist in possible_dists:
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

        # If any dist has perfect recipes, return it
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

        if not name and possible_dists:
            info('Asked for dist with name {} with recipes ({}), but a dist '
                 'with this name already exists and has incompatible recipes '
                 '({})'.format(name, ', '.join(recipes),
                               ', '.join(possible_dists[0].recipes)))
            info('No compatible dist found, so exiting.')
            exit(1)

        # # 2) Check if any downloadable dists meet the requirements

        # online_dists = [('testsdl2', ['hostpython2', 'sdl2_image',
        #                               'sdl2_mixer', 'sdl2_ttf',
        #                               'python2', 'sdl2',
        #                               'pyjniussdl2', 'kivysdl2'],
        #                  'https://github.com/inclement/sdl2-example-dist/archive/master.zip'),
        #                  ]
        # _possible_dists = []
        # for dist_name, dist_recipes, dist_url in online_dists:
        #     for recipe in recipes:
        #         if recipe not in dist_recipes:
        #             break
        #     else:
        #         dist = Distribution(ctx)
        #         dist.name = dist_name
        #         dist.url = dist_url
        #         _possible_dists.append(dist)
        # # if _possible_dists

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
                dists.append(dist)
        return dists

    def save_info(self):
        '''
        Save information about the distribution in its dist_dir.
        '''
        with current_directory(self.dist_dir):
            info('Saving distribution info')
            with open('dist_info.json', 'w') as fileh:
                json.dump({'dist_name': self.name,
                           'archs': [arch.arch for arch in self.ctx.archs],
                           'recipes': self.ctx.recipe_build_order},
                          fileh)

    def load_info(self):
        '''Load information about the dist from the info file that p4a
        automatically creates.'''
        with current_directory(self.dist_dir):
            filen = 'dist_info.json'
            if not exists(filen):
                return None
            with open('dist_info.json', 'r') as fileh:
                dist_info = json.load(fileh)
        return dist_info


def pretty_log_dists(dists, log_func=info):
    infos = []
    for dist in dists:
        infos.append('{Fore.GREEN}{Style.BRIGHT}{name}{Style.RESET_ALL}: '
                     'includes recipes ({Fore.GREEN}{recipes}'
                     '{Style.RESET_ALL}), built for archs ({Fore.BLUE}'
                     '{archs}{Style.RESET_ALL})'.format(
                         name=dist.name, recipes=', '.join(dist.recipes),
                         archs=', '.join(dist.archs) if dist.archs else 'UNKNOWN',
                         Fore=Err_Fore, Style=Err_Style))

    for line in infos:
        log_func('\t' + line)
