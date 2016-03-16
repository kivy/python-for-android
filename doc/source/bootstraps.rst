
Bootstraps
==========

python-for-android (p4a) supports multiple *bootstraps*. These fulfill a
similar role to recipes, but instead of describing how to compile a
specific module they describe how a full Android project may be put
together from a combination of individual recipes and other
components such as Android source code and various build files.

If you do not want to modify p4a, you don't need to worry about
bootstraps, just make sure you specify what modules you want to use
(or specify an existing bootstrap manually), and p4a will
automatically build everything appropriately. The existing choices are
explained on the :ref:`build options <bootstrap_build_options>` page.

This page describes the basics of how bootstraps work so that you can
create and use your own if you like, making it easy to build new kinds
of Python project for Android.
  

Creating a new bootstrap
------------------------

A bootstrap class consists of just a few basic components, though one of them must do a lot of work. 

For instance, the SDL2 bootstrap looks like the following::

    from pythonforandroid.toolchain import Bootstrap, shprint, current_directory, info, warning, ArchAndroid, logger, info_main, which
    from os.path import join, exists
    from os import walk
    import glob
    import sh


    class SDL2Bootstrap(Bootstrap):
        name = 'sdl2'

        recipe_depends = ['sdl2']

        def run_distribute(self):
            # much work is done here...

            
The declaration of the bootstrap name and recipe dependencies should
be clear. However, the :code:`run_distribute` method must do all the
work of creating a build directory, copying recipes etc into it, and
adding or removing any extra components as necessary.

If you'd like to create a bootstrap, the best resource is to check the
existing ones in the p4a source code. You can also :doc:`contact the
developers <troubleshooting>` if you have problems or questions.
