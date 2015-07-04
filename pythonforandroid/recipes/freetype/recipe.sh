#!/bin/bash

VERSION_freetype=${VERSION_freetype:-2.5.5}
DEPS_freetype=(harfbuzz)
URL_freetype=http://download.savannah.gnu.org/releases/freetype/freetype-2.5.5.tar.gz
MD5_freetype=7448edfbd40c7aa5088684b0a3edb2b8
BUILD_freetype=$BUILD_PATH/freetype/$(get_directory $URL_freetype)
RECIPE_freetype=$RECIPES_PATH/freetype

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_freetype() {
    true
}

function build_freetype() {
    cd $BUILD_freetype
    push_arm
    export LDFLAGS="$LDFLAGS -L$BUILD_harfbuzz/src/.libs/"
    try ./configure --host=arm-linux-androideabi --prefix=$BUILD_freetype --without-zlib --with-png=no --enable-shared
    try make -j5
    pop_arm

    try cp $BUILD_freetype/objs/.libs/libfreetype.so $LIBS_PATH
}

# function called after all the compile have been done
function postbuild_freetype() {
    true
}

