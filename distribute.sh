#!/bin/bash
#------------------------------------------------------------------------------
#
# Python for android
# https://github.com/tito/python-for-android
#
#------------------------------------------------------------------------------

# Modules
MODULES=$MODULES

# Paths
ROOT_PATH="$(dirname $(readlink -f $0))"
RECIPES_PATH="$ROOT_PATH/recipes"
BUILD_PATH="$ROOT_PATH/build"
LIBS_PATH="$ROOT_PATH/build/libs"
PACKAGES_PATH="$BUILD_PATH/packages"
SRC_PATH="$ROOT_PATH/src"
JNI_PATH="$SRC_PATH/jni"
DIST_PATH="$ROOT_PATH/dist"

# Internals
CRED="\x1b[31;01m"
CBLUE="\x1b[34;01m"
CGRAY="\x1b[30;01m"
CRESET="\x1b[39;49;00m"

# Use ccache ?
which ccache &>/dev/null
if [ $? -eq 0 ]; then
	export CC="ccache gcc"
	export CXX="ccache g++"
fi

#set -x

function try () {
    "$@" || exit -1
}

function info() {
	echo -e "$CBLUE"$@"$CRESET";
}

function error() {
	echo -e "$CRED"$@"$CRESET";
}

function debug() {
	echo -e "$CGRAY"$@"$CRESET";
}

function get_directory() {
	case $1 in
		*.tar.gz)	directory=$(basename $1 .tar.gz) ;;
		*.tgz)		directory=$(basename $1 .tgz) ;;
		*.tar.bz2)	directory=$(basename $1 .tar.bz2) ;;
		*.tbz2)		directory=$(basename $1 .tbz2) ;;
		*.zip)		directory=$(basename $1 .zip) ;;
		*)
			error "Unknown file extension $1"
			exit -1
			;;
	esac
	echo $directory
}

function push_arm() {
	info "Entering in ARM enviromnent"

	# save for pop
	export OLD_PATH=$PATH
	export OLD_CFLAGS=$CFLAGS
	export OLD_CXXFLAGS=$CXXFLAGS
	export OLD_CC=$CC
	export OLD_CXX=$CXX
	export OLD_AR=$AR
	export OLD_RANLIB=$RANLIB
	export OLD_STRIP=$STRIP
	export OLD_MAKE=$MAKE

	# to override the default optimization, set OFLAG
	#export OFLAG="-Os"
	#export OFLAG="-O2"

	export CFLAGS="-mandroid $OFLAG -fomit-frame-pointer --sysroot $NDKPLATFORM"
	if [ $ARCH == "armeabi-v7a" ]; then
		CFLAGS+=" -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -mthumb"
	fi
	export CXXFLAGS="$CFLAGS"

	# this must be something depending of the API level of Android
	export PATH="$ANDROIDNDK/toolchains/arm-eabi-4.4.0/prebuilt/linux-x86/bin/:$ANDROIDNDK:$ANDROIDSDK/tools:$PATH"
	if [ "X$ANDROIDNDKVER" == "Xr7"  ]; then
		export TOOLCHAIN_PREFIX=arm-linux-androideabi
		export TOOLCHAIN_VERSION=4.4.3
	elif [ "X$ANDROIDNDKVER" == "Xr5b" ]; then
		export TOOLCHAIN_PREFIX=arm-eabi
		export TOOLCHAIN_VERSION=4.4.0
	else
		error "Unable to configure NDK toolchain for NDK $ANDROIDNDKVER"
		exit -1
	fi

	export PATH="$ANDROIDNDK/toolchains/$TOOLCHAIN_PREFIX-$TOOLCHAIN_VERSION/prebuilt/linux-x86/bin/:$ANDROIDNDK:$ANDROIDSDK/tools:$PATH"
	export CC="$TOOLCHAIN_PREFIX-gcc $CFLAGS"
	export CXX="$TOOLCHAIN_PREFIX-g++ $CXXFLAGS"
	export AR="$TOOLCHAIN_PREFIX-ar" 
	export RANLIB="$TOOLCHAIN_PREFIX-ranlib"
	export STRIP="$TOOLCHAIN_PREFIX-strip --strip-unneeded"
	export MAKE="make -j5"

	# Use ccache ?
	which ccache &>/dev/null
	if [ $? -eq 0 ]; then
		export CC="ccache $CC"
		export CXX="ccache $CXX"
	fi
}

function pop_arm() {
	info "Leaving ARM enviromnent"
	export PATH=$OLD_PATH
	export CFLAGS=$OLD_CFLAGS
	export CXXFLAGS=$OLD_CXXFLAGS
	export CC=$OLD_CC
	export CXX=$OLD_CXX
	export AR=$OLD_AR
	export RANLIB=$OLD_RANLIB
	export STRIP=$OLD_STRIP
	export MAKE=$OLD_MAKE
}

function run_prepare() {
	info "Check enviromnent"
	if [ "X$ANDROIDSDK" == "X" ]; then
		error "No ANDROIDSDK environment set, abort"
		exit -1
	fi

	if [ "X$ANDROIDNDK" == "X" ]; then
		error "No ANDROIDNDK environment set, abort"
		exit -1
	fi

	if [ "X$ANDROIDAPI" == "X" ]; then
		export ANDROIDAPI=14
	fi

	if [ "X$ANDROIDNDKVER" == "X" ]; then
		error "No ANDROIDNDKVER enviroment set, abort"
		error "(Must be something like 'r5b', 'r7'...)"
		exit -1
	fi

	debug "SDK located at $ANDROIDSDK"
	debug "NDK located at $ANDROIDNDK"
	debug "NDK version is $ANDROIDNDKVER"
	debug "API level set to $ANDROIDAPI"

	export NDKPLATFORM="$ANDROIDNDK/platforms/android-$ANDROIDAPI/arch-arm"
	export ARCH="armeabi"
	#export ARCH="armeabi-v7a" # not tested yet.

	info "Check mandatory tools"
	# ensure that some tools are existing
	for tool in md5sum tar bzip2 unzip make gcc g++; do
		which $tool &>/dev/null
		if [ $? -ne 0 ]; then
			error "Tool $tool is missing"
			exit -1
		fi
	done

	# create build directory if not found
	if [ ! -d $BUILD_PATH ]; then
		mkdir -p $BUILD_PATH
		mkdir -p $LIBS_PATH
		mkdir -p $PACKAGES_PATH
	fi

	# create initial files
	echo "target=android-$ANDROIDAPI" > $SRC_PATH/default.properties
	echo "sdk.dir=$ANDROIDSDK" > $SRC_PATH/local.properties
}

function run_source_modules() {
	needed=(hostpython python $MODULES)
	declare -A processed

	while [ ${#needed[*]} -ne 0 ]; do

		# pop module from the needed list
		module=${needed[0]}
		unset needed[0]
		needed=( ${needed[@]} )

		# check if the module have already been declared
		if [[ ${processed[$module]} ]]; then
			debug "Ignored $module, already processed"
			continue;
		fi

		# add this module as done
		processed[$module]=1

		# read recipe
		debug "Read $module recipe"
		recipe=$RECIPES_PATH/$module/recipe.sh
		if [ ! -f $recipe ]; then
			error "Recipe $module does not exit"
			exit -1
		fi
		source $RECIPES_PATH/$module/recipe.sh

		# append current module deps to the needed
		deps=$(echo \$"{DEPS_$module[@]}")
		eval deps=($deps)
		if [ ${#deps[*]} -gt 0 ]; then
			debug "Module $module depend on" ${deps[@]}
			needed=( ${needed[@]} ${deps[@]} )
		fi
	done
}

# order modules by their priority
function run_order_modules() {
	cd $BUILD_PATH
	filename=$RANDOM.order
	if [ -f $filename ]; then
		rm $filename
	fi

	for module in hostpython python $MODULES; do
		# get priority
		priority="PRIORITY_$module"
		priority=${!priority}
		# write on the file
		echo "$priority $module" >> $filename
	done

	# update modules by priority
	MODULES=$(sort -n $filename|cut -d\  -f2)
	info "Module order is '$MODULES'"

	# remove temporary filename
	rm $filename
}

function run_get_deps() {
	info "Run get dependencies"

	for module in $MODULES; do
		# download dependencies for this module
		debug "Download dependencies for $module"

		url="URL_$module"
		url=${!url}
		md5="MD5_$module"
		md5=${!md5}

		if [ ! -d "$BUILD_PATH/$module" ]; then
			try mkdir -p $BUILD_PATH/$module
		fi

		if [ "X$url" == "X" ]; then
			debug "No dependencies for $module"
			continue
		fi

		filename=$(basename $url)
		do_download=1

		# check if the file is already present
		cd $PACKAGES_PATH
		if [ -f $filename ]; then

			# check if the md5 is correct
			current_md5=$(md5sum $filename | cut -d\  -f1)
			if [ "X$current_md5" == "X$md5" ]; then
				# correct, no need to download
				do_download=0
			else
				# invalid download, remove the file
				error "Module $module have invalid md5, redownload."
				rm $filename
			fi
		fi

		# download if needed
		if [ $do_download -eq 1 ]; then
			info "Downloading $url"
			try wget $url
		else
			debug "Module $module already downloaded"
		fi

		# check md5
		current_md5=$(md5sum $filename | cut -d\  -f1)
		if [ "X$current_md5" != "X$md5" ]; then
			error "File $filename md5 check failed (got $current_md5 instead of $md5)."
			error "Ensure the file is correctly downloaded, and update MD5S_$module"
			exit -1
		fi

		# if already decompress, forget it
		cd $BUILD_PATH/$module
		directory=$(get_directory $filename)
		if [ -d $directory ]; then
			continue
		fi

		# decompress
		pfilename=$PACKAGES_PATH/$filename
		info "Extract $pfilename"
		case $pfilename in
			*.tar.gz|*.tgz )
				try tar xzf $pfilename
				root_directory=$(basename $(try tar tzf $pfilename|head -n1))
				if [ "X$root_directory" != "X$directory" ]; then
					mv $root_directory $directory
				fi
				;;
			*.tar.bz2|*.tbz2 )
				try tar xjf $pfilename
				root_directory=$(basename $(try tar tjf $pfilename|head -n1))
				if [ "X$root_directory" != "X$directory" ]; then
					mv $root_directory $directory
				fi
				;;
			*.zip )
				try unzip x $pfilename
				root_directory=$(basename $(try unzip -l $pfilename|sed -n 4p|awk '{print $4}'))
				if [ "X$root_directory" != "X$directory" ]; then
					mv $root_directory $directory
				fi
				;;
		esac
	done
}

function run_prebuild() {
	info "Run prebuild"
	cd $BUILD_PATH
	for module in $MODULES; do
		fn=$(echo prebuild_$module)
		debug "Call $fn"
		$fn
	done
}

function run_build() {
	info "Run build"
	cd $BUILD_PATH
	for module in $MODULES; do
		fn=$(echo build_$module)
		debug "Call $fn"
		$fn
	done
}

function run_postbuild() {
	info "Run postbuild"
	cd $BUILD_PATH
	for module in $MODULES; do
		fn=$(echo postbuild_$module)
		debug "Call $fn"
		$fn
	done
}

function run_distribute() {
	info "Run distribute"

	if [ -e $DIST_PATH ]; then
		debug "Remove old distribution"
		try rm -rf $DIST_PATH
	fi

	debug "Create new distribution at $DIST_PATH"
	try mkdir -p $DIST_PATH
	cd $DIST_PATH

	debug "Create initial layout"
	try mkdir assets bin gen obj private res templates

	debug "Copy default files"
	try cp -a $SRC_PATH/default.properties .
	try cp -a $SRC_PATH/local.properties .
	try cp -a $SRC_PATH/build.py .
	try cp -a $SRC_PATH/buildlib .
	try cp -a $SRC_PATH/src .
	try cp -a $SRC_PATH/templates .
	try cp -a $SRC_PATH/res .

	debug "Copy python distribution"
	try cp -a $BUILD_PATH/python-install .

	debug "Copy libs"
	try mkdir -p libs/$ARCH
	try cp -a $BUILD_PATH/libs/* libs/$ARCH/

	debug "Fill private directory"
	try cp -a python-install/lib/python* private/lib
	try mv private/lib/lib-dynload/*.so private/

	debug "Reduce private directory from unwanted files"
	cd $DIST_PATH/private/lib
	try find . | grep -E '*\.(py|pyc|so\.o|so\.a|so\.libs)$' | xargs rm
	try rm -rf test
	try rm -rf ctypes
	try rm -rf lib2to3
	try rm -rf lib-tk
	try rm -rf idlelib
	try rm -rf unittest/test
	try rm -rf lib-dynload
	try rm -rf json/tests
	try rm -rf distutils/tests
	try rm -rf email/test
	try rm -rf bsddb/test
	try rm -rf distutils
	try rm -rf config/libpython*.a
	try rm -rf config/python.o
	try rm -rf curses

}

function run() {
	run_prepare
	run_source_modules
	run_order_modules
	run_get_deps
	run_prebuild
	run_build
	run_postbuild
	run_distribute
	info "All done !"
}

# Do the build
run

