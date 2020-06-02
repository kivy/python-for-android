import os
import sh
from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.util import (current_directory, ensure_dir)
from pythonforandroid.logger import (info, shprint)


class ReportLabRecipe(CompiledComponentsPythonRecipe):
    version = 'c088826211ca'
    url = 'https://bitbucket.org/rptlab/reportlab/get/{version}.tar.gz'
    depends = ['freetype']
    call_hostpython_via_targetpython = False

    def prebuild_arch(self, arch):
        if not self.is_patched(arch):
            super().prebuild_arch(arch)
            recipe_dir = self.get_build_dir(arch.arch)

            # Some versions of reportlab ship with a GPL-licensed font.
            # Remove it, since this is problematic in .apks unless the
            # entire app is GPL:
            font_dir = os.path.join(recipe_dir,
                                    "src", "reportlab", "fonts")
            if os.path.exists(font_dir):
                for file in os.listdir(font_dir):
                    if file.lower().startswith('darkgarden'):
                        os.remove(os.path.join(font_dir, file))

            # Apply patches:
            self.apply_patch('patches/fix-setup.patch', arch.arch)
            shprint(sh.touch, os.path.join(recipe_dir, '.patched'))
            ft = self.get_recipe('freetype', self.ctx)
            ft_dir = ft.get_build_dir(arch.arch)
            ft_lib_dir = os.environ.get('_FT_LIB_', os.path.join(ft_dir, 'objs', '.libs'))
            ft_inc_dir = os.environ.get('_FT_INC_', os.path.join(ft_dir, 'include'))
            tmp_dir = os.path.normpath(os.path.join(recipe_dir, "..", "..", "tmp"))
            info('reportlab recipe: recipe_dir={}'.format(recipe_dir))
            info('reportlab recipe: tmp_dir={}'.format(tmp_dir))
            info('reportlab recipe: ft_dir={}'.format(ft_dir))
            info('reportlab recipe: ft_lib_dir={}'.format(ft_lib_dir))
            info('reportlab recipe: ft_inc_dir={}'.format(ft_inc_dir))
            with current_directory(recipe_dir):
                ensure_dir(tmp_dir)
                pfbfile = os.path.join(tmp_dir, "pfbfer-20070710.zip")
                if not os.path.isfile(pfbfile):
                    sh.wget("http://www.reportlab.com/ftp/pfbfer-20070710.zip", "-O", pfbfile)
                sh.unzip("-u", "-d", os.path.join(recipe_dir, "src", "reportlab", "fonts"), pfbfile)
                if os.path.isfile("setup.py"):
                    with open('setup.py', 'r') as f:
                        text = f.read().replace('_FT_LIB_', ft_lib_dir).replace('_FT_INC_', ft_inc_dir)
                    with open('setup.py', 'w') as f:
                        f.write(text)


recipe = ReportLabRecipe()
