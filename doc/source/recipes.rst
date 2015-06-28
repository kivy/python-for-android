
Recipes
=======

This documentation describes how python-for-android (p4a) recipes
work. These are special scripts for installing different programs
(including Python modules) into a p4a distribution. They are necessary
to take care of compilation for any compiled components (which must be
compiled for Android with the correct architecture).

python-for-android comes with many recipes for popular modules, and no
recipe is necessary at all for the use of Python modules with no
compiled components; if you just want to build an APK, you can jump
straight to the :doc:`quickstart` or :doc:`commands` documentation, or
can use the :code:`recipes` command to list available recipes. 


Creating your own Recipe
------------------------

This documentation jumps straight to the practicalities of creating
your own recipe. The formal reference documentation of the Recipe
class can be found in the `Recipe class <recipe_class_>`_ section and below.

The basic declaration of a recipe is as follows::

  class YourRecipe(Recipe):

      url = 'http://example.com/example-{version}.tar.gz'
      version = '2.0.3'
      md5sum = '4f3dc9a9d857734a488bcbefd9cd64ed'

      depends = ['kivy', 'sdl2']  # These are just examples
      conflicts = ['pygame'] 
    
  recipe = YourRecipe()

See the `Recipe class documentation <recipe_class_>`_ for full
information about each parameter.

These core options are vital for all recipes, though the url may be
omitted if the source is somehow loaded from elsewhere.

The ``recipe = YourRecipe()`` is also vital. This variable is used
when the recipe is imported as the recipe instance to build with. If
it is omitted, your recipe won't work.

.. note:: The url includes the ``{version}`` tag. You should only
          access the url with the ``versioned_url`` property, which
          replaces this with the version attribute.

The actual build process takes place via three core methods::

      def prebuild_arch(self, arch):
          super(YourRecipe, self).prebuild_arch(arch)
          # Do any pre-initialisation

      def build_arch(self, arch):
          super(YourRecipe, self).build_arch(arch)
          # Do the main recipe build
         
      def postbuild_arch(self, arch):
          super(YourRecipe, self).build_arch(arch)
          # Do any clearing up

The prebuild of every recipe is run before the build of any recipe,
and likewise the build of every recipe is run before the postbuild of
any. This lets you strictly order the build process.

If you defined an url for your recipe, you do *not* need to manually
download it, this is handled automatically.

The recipe will automatically be built in a special isolated build
directory, which you can access with
:code:`self.get_build_dir(arch.arch)`. You should only work within
this directory. It may be convenient to use the ``current_directory``
context manager defined in toolchain.py::

  from toolchain import current_directory
  def build_arch(self, arch):
      super(YourRecipe, self).build_arch(arch)
      with current_directory(self.get_build_dir(arch.arch)):
          with open('example_file.txt', 'w'):
              fileh.write('This is written to a file within the build dir')
  
The argument to each method, ``arch``, is an object relating to the
architecture currently being built for. You can mostly ignore it,
though may need to use the arch name ``arch.arch``.
          
.. note:: You can also implement arch-specific versions of each
          method, which are called (if they exist) by the superclass,
          e.g. ``def prebuild_armeabi(self, arch)``.
          

This is the core of what's necessary to write a recipe, but has not
covered any of the details of how one actually writes code to compile
for android. This is covered in the next sections, including the
`standard mechanisms <standard_mechanisms_>`_ used as part of the
build, and the details of specific recipe classes for Python, Cython,
and some generic compiled recipes. If your module is one of the
latter, you should use these later classes rather than reimplementing
the functionality from scratch.

.. _standard_mechanisms:

Methods and tools to help with compilation
------------------------------------------

Patching modules before installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can easily apply patches to your recipes with the ``apply_patch``
method. For instance, you could do this in your prebuild method::

  import sh
  def prebuild_arch(self, arch):
       super(YourRecipe, self).prebuild_arch(arch)
       build_dir = self.get_build_dir(arch.arch)
       if exists(join(build_dir, '.patched')):
           print('Your recipe is already patched, skipping')
           return
       self.apply_patch('some_patch.patch')
       shprint(sh.touch, join(build_dir, '.patched'))

The path to the patch should be in relation to your recipe code.
In this case, ``some_path.patch`` must be in the same directory as the
recipe.

This code also manually takes care to patch only once. You can use the
same strategy yourself, though a more generic solution may be provided
in the future.

Compiling for the Android architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When performing any compilation, it is vital to do so with appropriate
environment variables set, ensuring that the Android libraries are
properly linked and the compilation target is the correct
architecture.

You can get a dictionary of appropriate environment variables with the
``get_recipe_env`` method. You should make sure to set this
environment for any processes that you call. It is convenient to do
this using the ``sh`` module as follows::

  def build_arch(self, arch):
      super(YourRecipe, self).build_arch(arch)
      env = self.get_recipe_env(arch)
      sh.echo('$PATH', _env=env)  # Will print the PATH entry fron the
                                  # env dict

You can also use the ``shprint`` helper function from the p4a
toolchain module, which will print information about the process and
its current status::

  from toolchain import shprint
  shprint(sh.echo, '$PATH', _env=env)

You can also override the ``get_recipe_env`` method to add new env
vars for the use of your recipe. For instance, the Kivy recipe does
the following when compiling for SDL2, in order to tell Kivy what
backend to use::

    def get_recipe_env(self, arch):
        env = super(KivySDL2Recipe, self).get_recipe_env(arch)
        env['USE_SDL2'] = '1'

        env['KIVY_SDL2_PATH'] = ':'.join([
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL', 'include'),
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_image'),
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_mixer'),
            join(self.ctx.bootstrap.build_dir, 'jni', 'SDL2_ttf'),
            ])
        return env
  
.. warning:: When using the sh module like this the new env *completely
          replaces* the normal environment, so you must define any env
          vars you want to access.
          
Including files with your recipe
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The should_build method
~~~~~~~~~~~~~~~~~~~~~~~
          

Using a PythonRecipe
--------------------

If your recipe is to install a Python module without compiled
components, you should use a PythonRecipe. This overrides
``build_arch`` to automatically call the normal ``python setup.py
install`` with an appropriate environment.

For instance, the following is all that's necessary to create a recipe
for the Vispy module::

  from toolchain import PythonRecipe
  class VispyRecipe(PythonRecipe):
      version = 'master'
      url = 'https://github.com/vispy/vispy/archive/{version}.zip'

      depends = ['python2', 'numpy']
      
      site_packages_name = 'vispy'

  recipe = VispyRecipe()
  
The ``site_packages_name`` is a new attribute that identifies the
folder in which the module will be installed in the Python
package. This is only essential to add if the name is different to the
recipe name. It is used to check if the recipe installation can be
skipped, which is the case if the folder is already present in the
Python installation.
  
For reference, the code that accomplishes this is the following::

    def build_arch(self, arch):
        super(PythonRecipe, self).build_arch(arch)
        self.install_python_package()

    def install_python_package(self):
        '''Automate the installation of a Python package (or a cython
        package where the cython components are pre-built).'''
        arch = self.filtered_archs[0]
        env = self.get_recipe_env(arch)

        info('Installing {} into site-packages'.format(self.name))

        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)

            shprint(hostpython, 'setup.py', 'install', '-O2', _env=env)
            
This combines techniques and tools from the above documentation to
create a generic mechanism for all Python modules.

.. note:: The hostpython is the path to the Python binary that should
          be used for any kind of installation. You *must* run Python
          in a similar way if you need to do so in any of your own
          recipes.


Using a CythonRecipe
--------------------

If your recipe is to install a Python module that uses Cython, you
should use a CythonRecipe. This overrides ``build_arch`` to both build
the cython components and to install the Python module just like a
normal PythonRecipe.

For instance, the following is all that's necessary to make a recipe
for Kivy (in this case, depending on Pygame rather than SDL2)::

  class KivyRecipe(CythonRecipe):
       version = 'stable'
       url = 'https://github.com/kivy/kivy/archive/{version}.zip'
       name = 'kivy'

       depends = ['pygame', 'pyjnius', 'android']

  recipe = KivyRecipe()
  
For reference, the code that accomplishes this is the following::

    def build_arch(self, arch):
        Recipe.build_arch(self, arch)  # a hack to avoid calling
                                       # PythonRecipe.build_arch
        self.build_cython_components(arch)
        self.install_python_package()  # this is the same as in a PythonRecipe

    def build_cython_components(self, arch):
        env = self.get_recipe_env(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            hostpython = sh.Command(self.ctx.hostpython)
            
            # This first attempt *will* fail, because cython isn't
            # installed in the hostpython
            try:
                shprint(hostpython, 'setup.py', 'build_ext', _env=env)
            except sh.ErrorReturnCode_1:
                pass

            # ...so we manually run cython from the user's system
            shprint(sh.find, self.get_build_dir('armeabi'), '-iname', '*.pyx', '-exec',
                    self.ctx.cython, '{}', ';', _env=env)

            # now cython has already been run so the build works
            shprint(hostpython, 'setup.py', 'build_ext', '-v', _env=env)

            # stripping debug symbols lowers the file size a lot
            build_lib = glob.glob('./build/lib*')
            shprint(sh.find, build_lib[0], '-name', '*.o', '-exec',
                    env['STRIP'], '{}', ';', _env=env)

The failing build and manual cythonisation is necessary, first to
make sure that any .pyx files have been generated by setup.py, and
second because cython isn't installed in the hostpython build.
 
Other than this, these methods follow the techniques in the above
documentation to make a generic recipe for most cython based modules.

Using a CompiledComponentsPythonRecipe
--------------------------------------

This is similar to a CythonRecipe but is intended for modules like
numpy which include compiled but non-cython components. It uses a
similar mechanism to compile with the right environment.

This isn't documented yet because it will probably be changed so that
CythonRecipe inherits from it (to avoid code duplication).

Using an NDKRecipe
------------------

If you are writing a recipe not for a Python module but for something
that would normall go in the JNI dir of an Android project (i.e. it
has an ``Application.mk`` and ``Android.mk`` that the Android build
system can use), you can use an NDKRecipe to automatically set it
up. The NDKRecipe overrides the normal ``get_build_dir`` method to
place things in the Android project.

.. warning:: The NDKRecipe does *not* currently actually call
             ndk-build, you must add this call (for your module) by
             manually making a build_arch method. This may be fixed
             later.

For instance, the following recipe is all that's necessary to place
SDL2_ttf in the jni dir. This is built later by the SDL2 recipe, which
calls ndk-build with this as a dependency::

 class LibSDL2TTF(NDKRecipe):
     version = '2.0.12'
     url = 'https://www.libsdl.org/projects/SDL_ttf/release/SDL2_ttf-{version}.tar.gz'
     dir_name = 'SDL2_ttf'

 recipe = LibSDL2TTF()

The dir_name argument is a new class attribute that tells the recipe
what the jni dir folder name should be. If it is omitted, the recipe
name is used. Be careful here, sometimes the folder name is important,
especially if this folder is a dependency of something else.

.. _recipe_class:

The ``Recipe`` class
--------------------

The ``Recipe`` is the base class for all p4a recipes. The core
documentation of this class is given below, followed by discussion of
how to create your own Recipe subclass.

.. autoclass:: toolchain.Recipe
   :members:
   :member-order: = 'bysource'



