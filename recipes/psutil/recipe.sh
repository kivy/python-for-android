#!/bin/bash

https://pypi.python.org/packages/source/p/psutil/psutil-0.6.1.tar.gz#md5=93c1420cb3dac091325a80c9c5ed9623

VERSION_psutil=${VERSION_psutil:-0.6.1}
DEPS_psutil=(python)
URL_psutil=http://pypi.python.org/packages/source/p/psutil/psutil-$VERSION_psutil.tar.gz
MD5_psutil=93c1420cb3dac091325a80c9c5ed9623
BUILD_psutil=$BUILD_PATH/psutil/$(get_directory $URL_psutil)
RECIPE_psutil=$RECIPES_PATH/psutil

# function called for preparing source code if needed
# (you can apply patch etc here.)
function prebuild_psutil() {
	cd $BUILD_psutil

	if [ -f .psutil_patched ]; then
	# no patch needed
	return
	fi

	try patch -p1 < $RECIPE_psutil/patches/psutil-$VERSION_psutil-android.patch

	# everything done
	touch .psutil_patched
}

function shouldbuild_psutil() {
    if [ -d "$SITEPACKAGES_PATH/psutil" ]; then
		DO_BUILD=0
	fi
}

function build_psutil() {
	cd $BUILD_psutil
	push_arm
	try $HOSTPYTHON setup.py build_ext -v
	try find build/lib.* -name "*.o" -exec $STRIP {} \;
	try $HOSTPYTHON setup.py install -O2
	pop_arm
}

# function called after all the compile have been done
function postbuild_psutil() {
	true
}

