from os.path import (exists, join, realpath, isdir, isfile,
                     basename, splitext)
import shutil
import os
import glob
import json
import sh
from sys import stdout

from pythonforandroid.logger import (info, info_notify, warning, error,
                                     Err_Style, Err_Fore, shprint)
from pythonforandroid.util import current_directory, urlretrieve


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
    def get_distribution(cls, ctx, name=None, recipes=[], allow_download=True,
                         force_build=False,
                         allow_build=True, extra_dist_dirs=[],
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
        allow_download : bool
            Whether binary dists may be downloaded.
        allow_build : bool
            Whether the distribution may be built from scratch if necessary.
            This is always False on e.g. Windows.
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

        # AND: This whole function is a bit hacky, it needs checking
        # properly to make sure it follows logically correct
        # possibilities

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


def import_binary_dist(path, ctx):
        path = realpath(path)

        filename, extension = splitext(basename(path))

        temp_dir = join(ctx.dist_dir, basename(filename))

        if not exists(path):
            error('No file or folder with the given name exists')
            exit(1)

        if exists(temp_dir):
            error('Cannot extract dist, a dist with the default temporary '
                  'name already exists')
            info('To fix this, rename the dist file or delete the existing '
                 'dist')
            exit(1)

        if isdir(path):
            info('Dist path is a directory, copying')
            shutil.copytree(path, temp_dir)
        elif isfile(path):
            info("Extracting {} into {}".format(path, temp_dir))

            if path.endswith(".tgz") or path.endswith(".tar.gz"):
                shprint(sh.tar, "-C", temp_dir, "-xvzf", path)

            elif path.endswith(".tbz2") or path.endswith(".tar.bz2"):
                shprint(sh.tar, "-C", temp_dir, "-xvjf", path)

            elif path.endswith(".zip"):
                import zipfile
                zf = zipfile.ZipFile(path)
                zf.extractall(path=temp_dir)
                zf.close()

        else:
            error(
                "Error: cannot extract, unrecognized filetype for {}"
                .format(path))
            exit(1)

        # Allow zipped dir or zipped contents
        files = os.listdir(temp_dir)
        if len(files) == 1:
            os.rename(temp_dir, temp_dir + '__old')
            os.rename(join(temp_dir + '__old', files[0]), temp_dir)
            shutil.rmtree(temp_dir + '__old')

        if not exists(join(temp_dir, 'dist_info.json')):
            error('Dist does not include a dist_info.json, cannot install')
            shutil.rmtree(temp_dir)
            exit(1)

        with open(join(temp_dir, 'dist_info.json'), 'r') as fileh:
            data = json.load(fileh)

        if 'dist_name' not in data:
            error('Dist does not have dist_name declared in its dist_info.json')
            shutil.rmtree(temp_dir)
            exit(1)

        dist_name = data['dist_name']
        info('Imported dist has name {}'.format(dist_name))

        dist_dir = join(ctx.dist_dir, dist_name)
        if dist_dir != temp_dir:
            if exists(dist_dir):
                error('A dist with this name already exists, exiting.')
                shutil.rmtree(temp_dir)
                exit(1)

            os.rename(temp_dir, dist_dir)
            
        info('Dist was imported successfully')
        info('Run `p4a dists` to see information about the new dist.')
    

def fetch_online_dists(ctx):
    dists_info = ('https://raw.githubusercontent.com/inclement/'
                  'p4a-binary-distribution/master/dists.json')

    if exists(join(ctx.storage_dir, 'binary_dists')):
        shutil.rmtree(join(ctx.storage_dir, 'binary_dists'))
    os.makedirs(join(ctx.storage_dir, 'binary_dists'))

    dists_info_filen = join(ctx.storage_dir, 'binary_dists', 'dists.json')

    if exists(dists_info_filen):
        os.unlink(dists_info_filen)

    def report_hook(index, blksize, size):
        if size <= 0:
            progression = '{0} bytes'.format(index * blksize)
        else:
            progression = '{0:.2f}%'.format(
                index * blksize * 100. / float(size))
        stdout.write('- Download {}\r'.format(progression))
        stdout.flush()

    urlretrieve(dists_info, dists_info_filen, report_hook)

    with open(dists_info_filen, 'r') as fileh:
        data = json.load(fileh)

    info('Retrieved binary dists index')

    info('Found dists for download:')
    for name, url in data:
        info('    - {}'.format(name))

    dists_to_import = []
    for name, url in data:
        if exists(join(ctx.dist_dir, name)):
            info('A dist with the name {} already exists, skipping.'.format(
                name))
            continue

        info('{} dist not yet present, downloading'.format(name))
        download_name = basename(url)
        urlretrieve(url, join(ctx.storage_dir, 'binary_dists', download_name),
                    report_hook)

        dists_to_import.append((name, url, join(ctx.storage_dir, 'binary_dists',
                                                download_name)))

    for name, url, path in dists_to_import:
        import_binary_dist(path, ctx)

    shutil.rmtree(join(ctx.storage_dir, 'binary_dists'))
