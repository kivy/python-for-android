from pythonforandroid.toolchain import Recipe


class SnappyRecipe(Recipe):
    version = '1.1.3'
    url = 'https://github.com/google/snappy/releases/download/{version}/snappy-{version}.tar.gz'

    def should_build(self, arch):
        # Only download to use in leveldb recipe
        return False


recipe = SnappyRecipe()
