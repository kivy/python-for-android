#!/bin/bash

VERSION_docutils=
URL_docutils=http://prdownloads.sourceforge.net/docutils/docutils-0.9.1.tar.gz
DEPS_docutils=(pil)
MD5_docutils=
BUILD_docutils=$BUILD_PATH/docutils/$(get_directory $URL_docutils)
RECIPE_docutils=$RECIPES_PATH/docutils

function prebuild_docutils() {
    true
}

function build_docutils() {
    if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/docutils" ]; then
        #return
        true
    fi

    cd $BUILD_docutils

    push_arm

    export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
    export LDSHARED="$LIBLINK"

    # fake try to be able to cythonize generated files
    $BUILD_PATH/python-install/bin/python.host setup.py build_ext
    try find . -iname '*.pyx' -exec cython {} \;
    try $BUILD_PATH/python-install/bin/python.host setup.py build_ext -v
    try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

    unset LDSHARED
    pop_arm
}

function postbuild_pyjnius() {
    true
}
