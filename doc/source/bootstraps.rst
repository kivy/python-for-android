
Bootstraps
==========

python-for-android (p4a) supports multiple *bootstraps*. These fulfil a
similar role to recipes, but instead of describing how to compile a
specific module they describe how a full Android project may be put
together from a combination of individual recipes and other
components such as Android source code and various build files.

If you do not want to modify p4a, you don't need to worry about
bootstraps, just make sure you specify what modules you want to use
(or specify an existing bootstrap manually), and p4a will
automatically build everything appropriately. 

This page describes the basics of how bootstraps work so that you can
create and use your own if you like, making it easy to build new kinds
of Python project for Android.


Current bootstraps
------------------

python-for-android includes the following bootstraps by default, which
may be chosen by name with a build parameter, or (by default) are
selected automatically in order to fulfil your build requirements. For
instance, if you add 'sdl2' in the requirements, the sdl2 backend will
be used.

p4a is designed to make it fairly easy to make your own bootstrap with a new backend,
e.g. one that creates a webview interface and runs python in the
background to serve a flask or django site from the phone itself.


pygame
%%%%%%

This builds APKs exactly like the old p4a toolchain, using Pygame as
the windowing and input backend.

This bootstrap automatically includes pygame, kivy, and python. It
could potentially be modified to work for non-Kivy projects.

sdl2
%%%%

This builds APKs using SDL2 as the window and input backend. It is not
fully developed compared to the Pygame backend, but has many
advantages and will be the long term default.

This bootstrap automatically includes SDL2, but nothing else.

You can use the sdl2 bootstrap to seamlessly make a Kivy APK, but can
also make Python apps using other libraries; for instance, using
pysdl2 and pyopengl. `Vispy <http://vispy.org/>`_ also runs on android
this way.

empty
%%%%%

This bootstrap has no dependencies and cannot actually build an
APK. It is useful for testing recipes without building unnecessary
components.
  

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

If you'd like to creat a bootstrap, the best resource is to check the
existing ones in the p4a source code. You can also :doc:`contact the
developers <troubleshooting>` if you have problems or questions.
