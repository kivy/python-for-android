import os, sh
from pythonforandroid.toolchain import CompiledComponentsPythonRecipe, warning
from pythonforandroid.util import (urlretrieve, current_directory, ensure_dir)
from pythonforandroid.logger import (logger, info, warning, error, debug, shprint, info_main)
class ReportLabRecipe(CompiledComponentsPythonRecipe):
    version = 'c088826211ca'
    url = 'https://bitbucket.org/rptlab/reportlab/get/{version}.tar.gz'
    depends = ['python2','freetype']

    def prebuild_arch(self, arch):
        if not self.is_patched(arch):
            super(ReportLabRecipe, self).prebuild_arch(arch)
            self.apply_patch('patches/fix-setup.patch',arch.arch)
            recipe_dir = self.get_build_dir(arch.arch)
            shprint(sh.touch, os.path.join(recipe_dir, '.patched'))
            ft = self.get_recipe('freetype',self.ctx)
            ft_dir = ft.get_build_dir(arch.arch)
            ft_lib_dir = os.environ.get('_FT_LIB_',os.path.join(ft_dir,'objs','.libs'))
            ft_inc_dir = os.environ.get('_FT_INC_',os.path.join(ft_dir,'include'))
            tmp_dir = os.path.normpath(os.path.join(recipe_dir,"..","..","tmp"))
            info('reportlab recipe: recipe_dir={}'.format(recipe_dir))
            info('reportlab recipe: tmp_dir={}'.format(tmp_dir))
            info('reportlab recipe: ft_dir={}'.format(ft_dir))
            info('reportlab recipe: ft_lib_dir={}'.format(ft_lib_dir))
            info('reportlab recipe: ft_inc_dir={}'.format(ft_inc_dir))
            with current_directory(recipe_dir):
                sh.ls('-lathr')
                ensure_dir(tmp_dir)
                pfbfile = os.path.join(tmp_dir,"pfbfer-20070710.zip")
                if not os.path.isfile(pfbfile):
                    sh.wget("http://www.reportlab.com/ftp/pfbfer-20070710.zip", "-O", pfbfile)
                sh.unzip("-u", "-d", os.path.join(recipe_dir, "src", "reportlab", "fonts"), pfbfile)
                if os.path.isfile("setup.py"):
                    with open('setup.py','rb') as f:
                        text = f.read().replace('_FT_LIB_',ft_lib_dir).replace('_FT_INC_',ft_inc_dir)
                    with open('setup.py','wb') as f:
                        f.write(text)

recipe = ReportLabRecipe()
