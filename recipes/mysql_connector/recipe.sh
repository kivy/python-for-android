#!/bin/bash

VERSION_mysql_connector=1.0.8
URL_mysql_connector=http://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-$VERSION_mysql_connector.tar.gz
DEPS_mysql_connector=()
MD5_mysql_connector=1f2dd335c72684d51ee5d34f127d7ca9
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
