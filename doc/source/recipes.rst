
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

This page describes how recipes work, and how to make your own.

