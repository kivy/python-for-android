
Recipes
=======

This page describes how python-for-android (p4a) compilation recipes
work, and how to build your own. If you just want to build an APK,
ignore this and jump straight to the :doc:`quickstart`.

Recipes are special scripts for compiling and installing different programs
(including Python modules) into a p4a distribution. They are necessary
to take care of compilation for any compiled components, as these must
be compiled for Android with the correct architecture.

python-for-android comes with many recipes for popular modules. No
recipe is necessary for Python modules which have no
compiled components; these are installed automatically via pip.
If you are new to building recipes, it is recommended that you first
read all of this page, at least up to the Recipe reference
documentation. The different recipe sections include a number of
examples of how recipes are built or overridden for specific purposes.


Creating your own Recipe
------------------------

The formal reference documentation of the Recipe
class can be found in the `Recipe class <recipe_class_>`_ section and below.

Check the `recipe template section <recipe_template_>`_ for a template
that combines all of these ideas, in which you can replace whichever
components you like.

The basic declaration of a recipe is as follows::

  class YourRecipe(Recipe):

      url = 'http://example.com/example-{version}.tar.gz'
      version = '2.0.3'
      md5sum = '4f3dc9a9d857734a488bcbefd9cd64ed'
      
      patches = ['some_fix.patch']  # Paths relative to the recipe dir

      depends = ['kivy', 'sdl2']  # These are just examples
      conflicts = ['generickndkbuild']
    
  recipe = YourRecipe()

See the `Recipe class documentation <recipe_class_>`_ for full
information about each parameter.

These core options are vital for all recipes, though the url may be
omitted if the source is somehow loaded from elsewhere.

You must include ``recipe = YourRecipe()``. This variable is accessed
when the recipe is imported.

.. note:: The url includes the ``{version}`` tag. You should only
          access the url with the ``versioned_url`` property, which
          replaces this with the version attribute.

The actual build process takes place via three core methods::

      def prebuild_arch(self, arch):
          super().prebuild_arch(arch)
          # Do any pre-initialisation

      def build_arch(self, arch):
          super().build_arch(arch)
          # Do the main recipe build
         
      def postbuild_arch(self, arch):
          super().build_arch(arch)
          # Do any clearing up

These methods are always run in the listed order; prebuild, then
build, then postbuild.

If you defined a url for your recipe, you do *not* need to manually
download it, this is handled automatically.

The recipe will automatically be built in a special isolated build
directory, which you can access with
:code:`self.get_build_dir(arch.arch)`. You should only work within
this directory. It may be convenient to use the ``current_directory``
context manager defined in toolchain.py::

  from pythonforandroid.toolchain import current_directory
  def build_arch(self, arch):
      super().build_arch(arch)
      with current_directory(self.get_build_dir(arch.arch)):
          with open('example_file.txt', 'w') as fileh:
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

You can easily apply patches to your recipes by adding them to the
``patches`` declaration, e.g.::

      patches = ['some_fix.patch',
                 'another_fix.patch']  
      
The paths should be relative to the recipe file. Patches are
automatically applied just once (i.e. not reapplied the second time
python-for-android is run).

You can also use the helper functions in ``pythonforandroid.patching``
to apply patches depending on certain conditions, e.g.::

  from pythonforandroid.patching import will_build, is_arch

  ...

  class YourRecipe(Recipe):
      
      patches = [('x86_patch.patch', is_arch('x86')),
                 ('sdl2_compatibility.patch', will_build('sdl2'))]

      ...
      
You can include your own conditions by passing any function as the
second entry of the tuple. It will receive the ``arch`` (e.g. x86,
armeabi) and ``recipe`` (i.e. the Recipe object) as kwargs. The patch
will be applied only if the function returns True.


Installing libs
~~~~~~~~~~~~~~~

Some recipes generate .so files that must be manually copied into the
android project. You can use code like the following to accomplish
this, copying to the correct lib cache dir::

    def build_arch(self, arch):
        do_the_build()  # e.g. running ./configure and make
        
        import shutil
        shutil.copyfile('a_generated_binary.so', 
                        self.ctx.get_libs_dir(arch.arch))
                        
Any libs copied to this dir will automatically be included in the
appropriate libs dir of the generated android project.

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
      super().build_arch(arch)
      env = self.get_recipe_env(arch)
      sh.echo('$PATH', _env=env)  # Will print the PATH entry from the
                                  # env dict

You can also use the ``shprint`` helper function from the p4a
toolchain module, which will print information about the process and
its current status::

  from pythonforandroid.toolchain import shprint
  shprint(sh.echo, '$PATH', _env=env)

You can also override the ``get_recipe_env`` method to add new env
vars for use in your recipe. For instance, the Kivy recipe does
the following when compiling for SDL2, in order to tell Kivy what
backend to use::

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)
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
    
The Recipe class has a ``should_build`` method, which returns a
boolean. This is called for each architecture before running
``build_arch``, and if it returns False then the build is
skipped. This is useful to avoid building a recipe more than once for
different dists.

By default, should_build returns True, but you can override it however
you like. For instance, PythonRecipe and its subclasses all replace it
with a check for whether the recipe is already installed in the Python
distribution::

    def should_build(self, arch):
        name = self.site_packages_name
        if name is None:
            name = self.name
        if self.ctx.has_package(name):
            info('Python package already exists in site-packages')
            return False
        info('{} apparently isn\'t already in site-packages'.format(name))
        return True



Using a PythonRecipe
--------------------

If your recipe is to install a Python module without compiled
components, you should use a PythonRecipe. This overrides
``build_arch`` to automatically call the normal ``python setup.py
install`` with an appropriate environment.

For instance, the following is all that's necessary to create a recipe
for the Vispy module::

  from pythonforandroid.recipe import PythonRecipe
  class VispyRecipe(PythonRecipe):
      version = 'master'
      url = 'https://github.com/vispy/vispy/archive/{version}.zip'

      depends = ['python3', 'numpy']
      
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
        super().build_arch(arch)
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
for Kivy::

  class KivyRecipe(CythonRecipe):
      version = 'stable'
      url = 'https://github.com/kivy/kivy/archive/{version}.zip'
      name = 'kivy'

      depends = ['sdl2', 'pyjnius']

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

The failing build and manual cythonisation is necessary, firstly to
make sure that any .pyx files have been generated by setup.py, and
secondly because cython isn't installed in the hostpython build.

This may actually fail if the setup.py tries to import cython before
making any .pyx files (in which case it crashes too early), although
this is probably not usually an issue. If this happens to you, try
patching to remove this import or make it fail quietly.
 
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
that would normally go in the JNI dir of an Android project (i.e. it
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

.. _recipe_template:

A Recipe template
-----------------

The following template includes all the recipe sections you might
use. None are compulsory, feel free to delete method
overrides if you do not use them::

    from pythonforandroid.toolchain import Recipe, shprint, current_directory
    from os.path import exists, join
    import sh
    import glob


    class YourRecipe(Recipe):
        # This could also inherit from PythonRecipe etc. if you want to
        # use their pre-written build processes

        version = 'some_version_string'
        url = 'http://example.com/example-{version}.tar.gz'
        # {version} will be replaced with self.version when downloading

        depends = ['python3', 'numpy']  # A list of any other recipe names
                                        # that must be built before this
                                        # one

        conflicts = []  # A list of any recipe names that cannot be built
                        # alongside this one

        def get_recipe_env(self, arch):
            env = super().get_recipe_env(arch)
            # Manipulate the env here if you want
            return env

        def should_build(self, arch):
            # Add a check for whether the recipe is already built if you
            # want, and return False if it is.
            return True

        def prebuild_arch(self, arch):
            super().prebuild_arch(self)
            # Do any extra prebuilding you want, e.g.:
            self.apply_patch('path/to/patch.patch')

        def build_arch(self, arch):
            super().build_arch(self)
            # Build the code. Make sure to use the right build dir, e.g.
            with current_directory(self.get_build_dir(arch.arch)):
                sh.ls('-lathr')  # Or run some commands that actually do
                                 # something

        def postbuild_arch(self, arch):
            super().prebuild_arch(self)
            # Do anything you want after the build, e.g. deleting
            # unnecessary files such as documentation


    recipe = YourRecipe()


Examples of recipes
-------------------

This documentation covers most of what is ever necessary to make a
recipe work. For further examples, python-for-android includes many
recipes for popular modules, which are an excellent resource to find
out how to add your own. You can find these in the `python-for-android
Github page
<https://github.com/kivy/python-for-android/tree/master/pythonforandroid/recipes>`__.


.. _recipe_class:

The ``Recipe`` class
--------------------

The ``Recipe`` is the base class for all p4a recipes. The core
documentation of this class is given below, followed by discussion of
how to create your own Recipe subclass.

.. autoclass:: toolchain.Recipe
   :members:
   :member-order: bysource



