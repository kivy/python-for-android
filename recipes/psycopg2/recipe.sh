#!/bin/bash

# There is a bug in storm that breaks with newer versions (>= 2.5)
VERSION_psycopg2=${VERSION_psycopg2:-2.4.5}
DEPS_psycopg2=(python libpq)
URL_psycopg2=http://pypi.python.org/packages/source/p/psycopg2/psycopg2-$VERSION_psycopg2.tar.gz
MD5_psycopg2=075e4df465e9a863f288d5bdf6e6887e
BUILD_psycopg2=$BUILD_PATH/psycopg2/$(get_directory $URL_psycopg2)
RECIPE_psycopg2=$RECIPES_PATH/psycopg2

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_psycopg2() {
    cd $BUILD_psycopg2
    if [ -f .patched ]; then
        return
    fi
    # Set the correct path where our cross compiled libpq.a is (otherwise it
    # will try to link against the system one)
    try sed -i "s|pg_config_helper.query(.libdir.)|'$LIBS_PATH'|" setup.py
    touch .patched
}

function shouldbuild_psycopg2() {
    if [ -d "$SITEPACKAGES_PATH/psycopg2" ]; then
        DO_BUILD=0
    fi
}

function build_psycopg2() {
    cd $BUILD_psycopg2
    push_arm
    export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
    export EXTRA_CFLAGS="--host linux-armv"
    # Statically compile psycopg
    try $HOSTPYTHON setup.py build_ext --static-libpq
    try $HOSTPYTHON setup.py install -O2 --root=$BUILD_PATH/python-install --install-lib=lib/python2.7/site-packages
    pop_arm
}

# function called after all the compile have been done
function postbuild_psycopg2() {
    true
}

