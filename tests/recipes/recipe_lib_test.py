from unittest import mock
from tests.recipes.recipe_ctx import RecipeCtx


class BaseTestForMakeRecipe(RecipeCtx):
    """
    An unittest for testing any recipe using the standard build commands
    (`configure/make`).

    .. note:: Note that Some cmake recipe may need some more specific testing
        ...but this should cover the basics.
    """

    recipe_name = None
    recipes = ["python3", "kivy"]
    recipe_build_order = ["hostpython3", "python3", "sdl2", "kivy"]
    expected_compiler = (
        "{android_ndk}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang"
    )

    sh_command_calls = ["./configure"]
    """The expected commands that the recipe runs via `sh.command`."""

    extra_env_flags = {}
    """
    This must be a dictionary containing pairs of key (env var) and value.
    """

    def __new__(cls, *args):
        obj = super(BaseTestForMakeRecipe, cls).__new__(cls)
        if obj.recipe_name is not None:
            print(f"We are testing recipe: {obj.recipe_name}")
            obj.recipes.append(obj.recipe_name)
            obj.recipe_build_order.insert(1, obj.recipe_name)
            return obj

    @mock.patch("pythonforandroid.recipe.Recipe.check_recipe_choices")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("pythonforandroid.archs.glob")
    @mock.patch("pythonforandroid.archs.find_executable")
    def test_get_recipe_env(
        self,
        mock_find_executable,
        mock_glob,
        mock_ensure_dir,
        mock_check_recipe_choices,
    ):
        """
        Test that get_recipe_env contains some expected arch flags and that
        some internal methods has been called.
        """
        mock_find_executable.return_value = self.expected_compiler.format(
                android_ndk=self.ctx._ndk_dir
        )
        mock_glob.return_value = ["llvm"]
        mock_check_recipe_choices.return_value = sorted(
            self.ctx.recipe_build_order
        )

        # make sure the arch flags are in env
        env = self.recipe.get_recipe_env(self.arch)
        for flag in self.arch.arch_cflags:
            self.assertIn(flag, env["CFLAGS"])
        self.assertIn(
            f"-target {self.arch.target}",
            env["CFLAGS"],
        )

        for flag, value in self.extra_env_flags.items():
            self.assertIn(value, env[flag])

        # make sure that the mocked methods are actually called
        mock_glob.assert_called()
        mock_ensure_dir.assert_called()
        mock_find_executable.assert_called()
        mock_check_recipe_choices.assert_called()

    @mock.patch("pythonforandroid.util.chdir")
    @mock.patch("pythonforandroid.build.ensure_dir")
    @mock.patch("pythonforandroid.archs.glob")
    @mock.patch("pythonforandroid.archs.find_executable")
    def test_build_arch(
        self,
        mock_find_executable,
        mock_glob,
        mock_ensure_dir,
        mock_current_directory,
    ):
        mock_find_executable.return_value = self.expected_compiler.format(
                android_ndk=self.ctx._ndk_dir
        )
        mock_glob.return_value = ["llvm"]
        with mock.patch(
            f"pythonforandroid.recipes.{self.recipe_name}.sh.Command"
        ) as mock_sh_command, mock.patch(
            f"pythonforandroid.recipes.{self.recipe_name}.sh.make"
        ) as mock_make:
            self.recipe.build_arch(self.arch)

            # make sure that the mocked methods are actually called
            mock_glob.assert_called()
            mock_ensure_dir.assert_called()
            mock_current_directory.assert_called()
            mock_find_executable.assert_called()
            for command in self.sh_command_calls:
                self.assertIn(
                    mock.call(command),
                    mock_sh_command.mock_calls,
                )
            mock_make.assert_called()