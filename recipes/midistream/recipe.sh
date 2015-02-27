#!/bin/bash

VERSION_midistream=${VERSION_midistream:-master}
URL_midistream=https://github.com/b3b/midistream/archive/${VERSION_midistream}.zip
DEPS_midistream=(python pyjnius audiostream)
MD5_midistream=
BUILD_midistream=$BUILD_PATH/midistream/$(get_directory $URL_midistream)
RECIPE_midistream=$RECIPES_PATH/midistream

function prebuild_midistream() {
    cd $BUILD_PATH/midistream
}

function shouldbuild_midistream() {
	if [ -d "$SITEPACKAGES_PATH/midistream" ]; then
		DO_BUILD=0
	fi
}

function build_midistream() {
    cd $BUILD_midistream

    push_arm

    # create fake (empty) shared library libsonivox.so
    echo | $CC -shared -o "$BUILD_PATH/libsonivox.so" -fPIC -xc - || exit -1

    export LDFLAGS="$LDFLAGS -lsonivox -L$BUILD_PATH"
    try find . -iname '*.pyx' -exec cython {} \;
    try $HOSTPYTHON setup.py build_ext -v
    try $HOSTPYTHON setup.py install

    pop_arm
}

function postbuild_midistream() {
	true
}
