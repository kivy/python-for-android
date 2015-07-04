
Commands
========

This page documents all the commands and options that can be passed to
toolchain.py.


Main commands
-------------

.. autoclass:: toolchain.ToolchainCL
   :members:


General arguments
-----------------

These arguments may be passed to any command in order to modify its behaviour.

``--debug``
  Print extra debug information about the build, including all compilation output.


Distribution arguments
----------------------

p4a supports several arguments used for specifying which compiled
Android distribution you want to use. You may pass any of these
arguments to any command, and if a distribution is required they will
be used to load, or compile, or download this as necessary.

None of these options are essential, and in principle you need only
supply those that you need.


``--name NAME``
  The name of the distribution. Only one distribution with a given name can be created.

``--requirements LIST,OF,REQUIREMENTS`` 
  The recipes that your
  distribution must contain, as a comma separated list. These must be
  names of recipes or the pypi names of Python modules.

``--force_build BOOL``
  Whether the distribution must be compiled from scratch.

.. note:: These options are preliminary. Others will include toggles
          for allowing downloads, and setting additional directories
          from which to load user dists.
