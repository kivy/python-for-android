#!/bin/bash

VERSION_docutils=${VERSION_docutils:-0.9.1}
URL_docutils=http://prdownloads.sourceforge.net/docutils/docutils-$VERSION_docutils.tar.gz
DEPS_docutils=(pil)
MD5_docutils=
BUILD_docutils=$BUILD_PATH/docutils/$(get_directory $URL_docutils)
RECIPE_docutils=$RECIPES_PATH/docutils

function prebuild_docutils() {
    true
}

function shouldbuild_docutils() {
	if [ -d "$SITEPACKAGES_PATH/docutils" ]; then
		DO_BUILD=0
	fi
}

function build_docutils() {
    cd $BUILD_docutils

    push_arm

    export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
    export LDSHARED="$LIBLINK"

    # fake try to be able to cythonize generated files
    $HOSTPYTHON setup.py build_ext
    try find . -iname '*.pyx' -exec $CYTHON {} \;
    try $HOSTPYTHON setup.py build_ext -v
    try $HOSTPYTHON setup.py install -O2

    unset LDSHARED
    pop_arm
}

function postbuild_docutils() {
    true
}
