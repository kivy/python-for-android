
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

See the `Recipe class documentation <recipe_class_>`_ for full
information about each parameter.

These core options are vital for all recipes, though the url may be
omitted if the source is somehow loaded from elsewhere.

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


.. _recipe_class:


The ``Recipe`` class
--------------------

The ``Recipe`` is the base class for all p4a recipes. The core
documentation of this class is given below, followed by discussion of
how to create your own Recipe subclass.

.. autoclass:: toolchain.Recipe
   :members:
   :member-order: = 'bysource'



