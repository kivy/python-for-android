#!/bin/bash

VERSION_pyyaml=${VERSION_pyyaml:-3.11}
DEPS_pyyaml=(libyaml python)
URL_pyyaml=http://pyyaml.org/download/pyyaml/PyYAML-$VERSION_pyyaml.tar.gz
MD5_pyyaml=f50e08ef0fe55178479d3a618efe21db
BUILD_pyyaml=$BUILD_PATH/pyyaml/$(get_directory $URL_pyyaml)
RECIPE_pyyaml=$RECIPES_PATH/pyyaml

function prebuild_pyyaml() {
	true
}

function shouldbuild_pyyaml() {
	if [ -d "$SITEPACKAGES_PATH/pyyaml" ]; then
		DO_BUILD=0
	fi
}

function build_pyyaml() {
	cd $BUILD_pyyaml
	push_arm
	export CC="$CC -I$BUILD_libyaml/include"
	export LDFLAGS="$LDFLAGS -L$LIBS_PATH"
	export LDSHARED="$LIBLINK"
	export PYTHONPATH=$BUILD_hostpython/Lib/site-packages

	# with C extension
	$HOSTPYTHON setup.py --with-libyaml install >/tmp/pyyaml-setup

	# pure python
#	$HOSTPYTHON setup.py --without-libyaml install

	unset LDSHARED
	pop_arm
}

function postbuild_pyyaml() {
	true
}

