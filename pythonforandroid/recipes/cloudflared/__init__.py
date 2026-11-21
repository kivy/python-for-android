from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.logger import info
# from subprocess import Popen


class CloudflaredRecipe(PythonRecipe):

    version = "1.4.0"
    url = "https://github.com/SNEHASISHROY-125/cloudflared4kivy/releases/download/latest/cloudflared-{version}.tar.gz"
    depends = ["pyjnius", "libcloudflared"]
    site_packages_name = "cloudflared"

    def build_arch(self, arch):
        super().build_arch(arch)
        info(f"done building cloudflared-{self.version}")


recipe = CloudflaredRecipe()