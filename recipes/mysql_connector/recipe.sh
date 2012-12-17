#!/bin/bash

VERSION_mysql_connector=1.0.7
URL_mysql_connector=https://launchpad.net/debian/+archive/primary/+files/mysql-connector-python_$VERSION_mysql_connector.orig.tar.gz
DEPS_mysql_connector=()
MD5_mysql_connector=44c6b2c314c7ab7b7060484970b5ff23
BUILD_mysql_connector=$BUILD_PATH/mysql_connector/$(get_directory $URL_mysql_connector)
RECIPE_mysql_connector=$RECIPES_PATH/mysql_connector

function prebuild_mysql_connector() {
	true
}

function build_mysql_connector() {
	cd $BUILD_mysql_connector
	ls
	push_arm

	try $BUILD_PATH/python-install/bin/python.host setup.py install -O2

	pop_arm
}

function postbuild_mysql_connector() {
	true
}
