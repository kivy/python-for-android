#!/bin/bash
# This recipe builds libtorrent-rasterbat with it's Python bindings
# It depends on Boost.Build and the source of several Boost libraries present in BOOST_ROOT, which is all provided by the boost recipe
VERSION_libtorrent=${VERSION_libtorrent:-1.0.5}
DEPS_libtorrent=(boost python)
URL_libtorrent=http://downloads.sourceforge.net/project/libtorrent/libtorrent/libtorrent-rasterbar-${VERSION_libtorrent}.tar.gz
MD5_libtorrent=d09521d34092ba430f430572c9e2b3d3
BUILD_libtorrent=$BUILD_PATH/libtorrent/$(get_directory $URL_libtorrent)
RECIPE_libtorrent=$RECIPES_PATH/libtorrent

function prebuild_libtorrent() {
	true
}

function shouldbuild_libtorrent() {
	if [ -f "$SITEPACKAGES_PATH/libtorrent.so" ]; then
		DO_BUILD=0
	fi
}

function build_libtorrent() {
	cd $BUILD_libtorrent/bindings/python

	push_arm

	# Some flags and stuff that I don't want here, but in user-config, but doesn't work otherwise
	BOOSTSTUFF="--sysroot=$ANDROIDNDK/platforms/android-$ANDROIDAPI/arch-arm -L$ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/libs/$ARCH -L$BUILD_PATH/python-install/lib -lpython2.7 -lgnustl_shared"
	
	# Build the Python bindings with Boost.Build and some dependencies recursively (libtorrent-rasterbar, Boost.*)
	# Also link to openssl
	$BOOST_ROOT/b2 -q -j$MAKE_JOBS target-os=android link=static boost-link=static boost=source threading=multi toolset=gcc-android geoip=off encryption=tommath linkflags="$BOOSTSTUFF" release
	
	# Copy the module
	try cp -L libtorrent.so $SITEPACKAGES_PATH
	
	pop_arm
}

function postbuild_libtorrent() {
	true
}
