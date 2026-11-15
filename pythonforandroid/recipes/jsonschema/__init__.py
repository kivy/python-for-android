import os
import sys

import sh

from pythonforandroid.logger import shprint
from pythonforandroid.recipe import PythonRecipe


class JsonschemaRecipe(PythonRecipe):
    name = "jsonschema"
    version = "4.17.3"
    url = None
    depends = []

    def build_arch(self, arch):
        env = {k: v for k, v in os.environ.items()
               if k not in ("PYTHONHOME", "PYTHONPATH", "PYTHONNOUSERSITE")}
        shprint(
            sh.Command(sys.executable), "-m", "pip", "install",
            f"{self.name}=={self.version}",
            "--target", self.ctx.get_python_install_dir(arch.arch),
            "--only-binary", ":all:",
            _env=env,
        )


recipe = JsonschemaRecipe()
