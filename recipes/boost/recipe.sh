#!/bin/bash
# This recipe only downloads Boost and builds Boost.Build
# Since Boost by default uses version numbers in the library names, it makes linking to them harder (as Android does not accept version numbers)
# This is used in the libtorrent recipe and Boost.Build is used to (recursivly) compile Boost from the source here
VERSION_boost=${VERSION_boost:-1.58.0}
DEPS_boost=(python)
URL_boost=http://downloads.sourceforge.net/project/boost/boost/${VERSION_boost}/boost_1_58_0.tar.gz # Don't forget to change the URL when changing the version
MD5_boost=5a5d5614d9a07672e1ab2a250b5defc5
BUILD_boost=$BUILD_PATH/boost/$(get_directory $URL_boost)
RECIPE_boost=$RECIPES_PATH/boost

function prebuild_boost() {
	cd $BUILD_boost

	# Boost config locations
	RECIPECONFIG=${RECIPE_boost}/user-config.jam
	BOOSTCONFIG=${BUILD_boost}/tools/build/src/user-config.jam

	# Make Boost.Build
	./bootstrap.sh --with-python=$HOSTPYTHON --with-python-root=$BUILD_PATH/python-install --with-python-version=2.7

	# Place our own user-config in Boost.Build and set the PYTHON_INSTALL variable, delete any previous copy first, so that is can be modified when the build directory still exists
	if [ -e ${BOOSTCONFIG} ]; then
		try rm ${BOOSTCONFIG}
	fi
	try cp ${RECIPECONFIG} ${BOOSTCONFIG}

	# Replace the generated project-config with our own
	try rm $BUILD_boost/project-config.jam*
	try cp $RECIPE_boost/project-config.jam $BUILD_boost
	
	# Create Android case for library linking when building Boost.Python
	#FIXME: Not idempotent
	sed -i "622i\ \ \ \ \ \ \ \ case * : return ;" tools/build/src/tools/python.jam
}

function build_boost() {
	cd $BUILD_boost
	
	# Export the Boost location to other recipes that want to know where to find Boost
	export BOOST_ROOT=$BUILD_boost
	# Export PYTHON_INSTALL as it is used in user-config
	export PYTHON_INSTALL="$BUILD_PATH/python-install"
	
	# Also copy libgnustl
	try cp $ANDROIDNDK/sources/cxx-stl/gnu-libstdc++/$TOOLCHAIN_VERSION/libs/$ARCH/libgnustl_shared.so $LIBS_PATH

	pop_arm
}

function postbuild_boost() {
	unset BOOST_ROOT
	unset PYTHONINSTALL
}
