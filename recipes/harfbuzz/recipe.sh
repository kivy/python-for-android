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
    try ./configure --without-icu --host=arm-linux-androideabi --prefix="$BUILD_PATH/python-install" --without-freetype --without-glib
    try make -j5
    pop_arm
}

# function called after all the compile have been done
function postbuild_harfbuzz() {
    ln -s $BUILD_freetype "$BUILD_PATH/freetype2"
    if [ -f "$BUILD_freetype/objs/.libs/libfreetype.so" ]; then
        echo "freetype found rebuilding harfbuzz with freetype support";
	#true
	echo $BUILD_PATH;
    #build again now that freetype has finished
    cd $BUILD_harfbuzz
    echo $BUILD_freetype;
    ls $BUILD_freetype;
    
    export LDFLAGS="-L$BUILD_freetype/objs/.libs/ $LDFLAGS"
    export CFLAGS="-I$BUILD_freetype/include/ -I$BUILD_freetype/ -I$BUILD_PATH/python-install/include/python2.7 $CFLAGS"
    export CPPFLAGS="-I$BUILD_freetype/include/ -I$BUILD_PATH/python-install/include/python2.7 $CPPFLAGS"
    export CC="-I$BUILD_freetype/include/ $CC "
    export LDSHARED="$LIBLINK"
    push_arm
    try ./configure --without-icu --host=arm-linux-androideabi --cross-compile --prefix="$BUILD_PATH/python-install" --without-glib --libdir="$BUILD_freetype/objs/.libs/" --includedir="$BUILD_freetype/include/"
    try make  --include-dir="$BUILD_freetype/include/" #-j5
    pop_arm
    try cp -L $BUILD_harfbuzz/src/.libs/libharfbuzz.so $LIBS_PATH
    fi
}

