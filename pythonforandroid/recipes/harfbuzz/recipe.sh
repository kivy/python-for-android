#!/bin/bash

VERSION_harfbuzz=${VERSION_harfbuzz:-2.5.5}
URL_harfbuzz=http://www.freedesktop.org/software/harfbuzz/release/harfbuzz-0.9.40.tar.bz2
MD5_harfbuzz=0e27e531f4c4acff601ebff0957755c2
BUILD_harfbuzz=$BUILD_PATH/harfbuzz/$(get_directory $URL_harfbuzz)
RECIPE_harfbuzz=$RECIPES_PATH/harfbuzz

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_harfbuzz() {
    true
}

function shouldbuild_harfbuzz() {
    if [ -f "$BUILD_harfbuzz/src/.libs/libharfbuzz.so" ]; then
        DO_BUILD=0
    fi
}

function build_harfbuzz() {
    cd $BUILD_harfbuzz

    push_arm
	#~ export LDFLAGS="-L$LIBS_PATH"
	#~ export LDSHARED="$LIBLINK"
    #try ./configure --build=i686-pc-linux-gnu --host=arm-linux-androideabi --prefix="$BUILD_PATH/python-install" --enable-shared --without-freetype --without-glib
    #~ try ./autogen.sh  --build=i686-pc-linux-gnu --host=arm-linux-androideabi --prefix="$BUILD_PATH/python-install" --without-freetype --without-glib
    try ./configure --without-icu --host=arm-linux-androideabi --prefix="$BUILD_PATH/python-install" --without-freetype --without-glib
    try make -j5
    pop_arm
    try cp -L $BUILD_harfbuzz/src/.libs/libharfbuzz.so $LIBS_PATH
}

# function called after all the compile have been done
function postbuild_harfbuzz() {
    true
}

