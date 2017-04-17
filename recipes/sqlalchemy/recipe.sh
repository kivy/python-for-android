#!/bin/bash

# version of your package
VERSION_sqlalchemy=0.7

# dependencies of this recipe
DEPS_sqlalchemy=(python setuptools)

# url of the package
URL_sqlalchemy=https://dl.dropboxusercontent.com/u/26205750/SQLAlchemy-0.8.2.tar.gz

# default build path
BUILD_sqlalchemy=$BUILD_PATH/sqlalchemy/$(get_directory $URL_sqlalchemy)

# default recipe path
RECIPE_sqlalchemy=$RECIPES_PATH/sqlalchemy

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_sqlalchemy() {
    
    cd $BUILD_sqlalchemy

    if [ -f .patched ]; then
        return
    fi

    try patch setup.py < $RECIPE_sqlalchemy/patches/first.patch

    touch .patched

}

# function called to build the source code
function build_sqlalchemy() {

    if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/sqlalchemy " ]; then
        return
    fi

    cd $BUILD_sqlalchemy

    push_arm

    export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
    export LDSHARED="$LIBLINK"

    #cythonize
    try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
    try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

    unset LDSHARED

    pop_arm

}

# function called after all the compile have been done
function postbuild_sqlalchemy() {
	true
}
