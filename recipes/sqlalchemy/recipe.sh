#!/bin/bash

VERSION_sqlalchemy=0.8.2
DEPS_sqlalchemy=(python)
URL_sqlalchemy=https://pypi.python.org/packages/source/S/SQLAlchemy/SQLAlchemy-${VERSION_sqlalchemy}.tar.gz
MD5_sqlalchemy=5a33fb43dea93468dbb2a6562ee80b54
BUILD_sqlalchemy=$BUILD_PATH/sqlalchemy/$(get_directory "${URL_sqlalchemy}")
RECIPE_sqlalchemy=$RECIPES_PATH/sqlalchemy

function prebuild_sqlalchemy() {
	true
}


function build_sqlalchemy() {
	if [ -d "$BUILD_PATH/python-install/lib/python2.7/site-packages/sqlalchemy" ]; then
		return
	fi

	cd $BUILD_sqlalchemy
	
	push_arm

	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	pop_arm
}


function postbuild_sqlalchemy() {
	true
}