"""Build AIOHTTP"""
from typing import List
from pythonforandroid.recipe import CythonRecipe  # type: ignore


class AIOHTTPRecipe(CythonRecipe):  # type: ignore # pylint: disable=R0903
    """Build AIOHTTP"""

    version = "v3.8.0"
    url = "https://github.com/aio-libs/aiohttp/archive/{version}.zip"
    name = "aiohttp"

    depends: List[str] = ["setuptools"]


recipe = AIOHTTPRecipe()
