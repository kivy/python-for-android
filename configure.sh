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
PACKAGES_PATH="$BUILD_PATH/packages"

# Internals
CRED="\x1b[31;01m"
CBLUE="\x1b[34;01m"
CGRAY="\x1b[30;01m"
CRESET="\x1b[39;49;00m"

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
	# ANDROIDSDK / ANDROIDNDK
	#export NDK="$PGS4A_ROOT/android-ndk-r5b"
	#export SDK="$PGS4A_ROOT/android-sdk-linux_86/"
	export NDKPLATFORM="$ANDROIDNDK/platforms/android-5/arch-arm"

	# save for pop
	export OLD_PATH=$PATH
	export OLD_ARCH=$ARCH
	export OLD_CFLAGS=$CFLAGS
	export OLD_CXXFLAGS=$CXXFLAGS
	export OLD_CC=$CC
	export OLD_CXX=$CXX
	export OLD_AR=$AR
	export OLD_RANLIB=$RANLIB
	export OLD_STRIP=$STRIP
	export OLD_MAKE=$MAKE

	export PATH="$NDK/toolchains/arm-eabi-4.4.0/prebuilt/linux-x86/bin/:$NDK:$SDK/tools:$PATH"
	export ARCH="armeabi"
	#export ARCH="armeabi-v7a"
	# to override the default optimization, set OFLAG
	#export OFLAG="-Os"
	#export OFLAG="-O2"

	export CFLAGS="-mandroid $OFLAG -fomit-frame-pointer --sysroot $NDKPLATFORM"
	if [ $ARCH == "armeabi-v7a" ]; then
		CFLAGS+=" -march=armv7-a -mfloat-abi=softfp -mfpu=vfp -mthumb"
	fi
	export CXXFLAGS="$CFLAGS"

	export CC="arm-eabi-gcc $CFLAGS"
	export CXX="arm-eabi-g++ $CXXFLAGS"
	export AR="arm-eabi-ar" 
	export RANLIB="arm-eabi-ranlib"
	export STRIP="arm-eabi-strip --strip-unneeded"
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
	export ARCH=$OLD_ARCH
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
		mkdir -p $PACKAGES_PATH
	fi
}
	
function run_source_modules() {
	for module in hostpython python $MODULES; do
		recipe=$RECIPES_PATH/$module/recipe.sh
		if [ ! -f $recipe ]; then
			error "Recipe $module does not exit"
			exit -1
		fi
		source $RECIPES_PATH/$module/recipe.sh
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
	info "Module order is $MODULES"

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
		filename=$(basename $url)
		do_download=1

		if [ ! -d "$BUILD_PATH/$module" ]; then
			try mkdir -p $BUILD_PATH/$module
		fi
		cd $PACKAGES_PATH

		# check if the file is already present
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
		case $filename in
			*.tar.gz|*.tgz ) try tar xzf $PACKAGES_PATH/$filename ;;
			*.tar.bz2|*.tbz2 ) try tar xjf $PACKAGES_PATH/$filename ;;
			*.zip ) try unzip x $PACKAGES_PATH/$filename ;;
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

function run() {
	run_prepare
	run_source_modules
	run_order_modules
	run_get_deps
	run_prebuild
	run_build
	run_postbuild
	info "All done !"
}

# Do the build
run

