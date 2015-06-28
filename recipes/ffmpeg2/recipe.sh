#!/bin/bash
# Recent change made ffmpeg2 not compatible with python-for-android yet.
# Only h264+aac build are working.

VERSION_ffmpeg2=${VERSION_ffmpeg2:-2.7.1}
URL_ffmpeg2=http://ffmpeg.org/releases/ffmpeg-$VERSION_ffmpeg2.tar.bz2
DEPS_ffmpeg2=()
MD5_ffmpeg2=
BUILD_ffmpeg2=$BUILD_PATH/ffmpeg2/$(get_directory $URL_ffmpeg2)
RECIPE_ffmpeg2=$RECIPES_PATH/ffmpeg2
ARCH_ffmpeg2=${ARCH_ffmpeg2:-armv7a}

function prebuild_ffmpeg2() {
	true
}

function shouldbuild_ffmpeg2() {
	if [ -f "$BUILD_ffmpeg2/build/ffmpeg/armeabi-v7a/lib/libavcodec.so" ]; then
		DO_BUILD=0
	fi
}

function build_ffmpeg2() {
	cd $BUILD_ffmpeg2

	# build ffmpeg2
	export NDK=$ANDROIDNDK
	push_arm

	# configure
	DEST=build/ffmpeg

	for version in $ARCH_ffmpeg2; do

	FLAGS="--disable-everything"
	FLAGS="$FLAGS --enable-parser=h264,aac"
	FLAGS="$FLAGS --enable-decoder=h263,h264,aac"
	FLAGS="$FLAGS --enable-filter=aresample,resample,crop"
	FLAGS="$FLAGS --enable-protocol=file,http"
	FLAGS="$FLAGS --enable-demuxer=sdp --enable-pic"
	FLAGS="$FLAGS --enable-small"
	FLAGS="$FLAGS --enable-hwaccels"
	FLAGS="$FLAGS --disable-static --enable-shared"
	# libpostproc is GPL: https://ffmpeg.org/pipermail/ffmpeg-user/2012-February/005162.html
	FLAGS="$FLAGS --enable-gpl"

	# needed to prevent _ffmpeg.so: version node not found for symbol av_init_packet@LIBAVFORMAT_52
	# /usr/bin/ld: failed to set dynamic section sizes: Bad value
	FLAGS="$FLAGS --disable-symver"

	# disable some unused algo
	# note: "golomb" are the one used in our video test, so don't use --disable-golomb
	# note: and for aac decoding: "rdft", "mdct", and "fft" are needed
	FLAGS="$FLAGS --disable-dxva2 --disable-vdpau --disable-vaapi"
	FLAGS="$FLAGS --disable-dct"

	# disable binaries / doc
	FLAGS="$FLAGS --disable-ffmpeg --disable-ffplay --disable-ffprobe --disable-ffserver"
	FLAGS="$FLAGS --disable-doc"

	case "$version" in
		x86)

			EXTRA_CFLAGS=""
			#EXTRA_LDFLAGS="-Wl,-Bsymbolic"
			EXTRA_LDFLAGS=""
			ABI="x86"
			;;
		armv7a)
			ARM_FLAGS="--target-os=android --cross-prefix=arm-linux-androideabi- --arch=arm"
			ARM_FLAGS="$ARM_FLAGS --sysroot=$NDKPLATFORM"
			FLAGS="$ARM_FLAGS $FLAGS"
			FLAGS="$FLAGS --enable-neon"
			EXTRA_CFLAGS="-march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp -fPIC -DANDROID"
			EXTRA_LDFLAGS=""
			ABI="armeabi-v7a"
			;;
		*)
			echo "Unknown platform $version"
			exit 1
			;;
	esac
	DEST="$DEST/$ABI"
	FLAGS="$FLAGS --prefix=$DEST"

	mkdir -p $DEST
	make distclean
	try ./configure $FLAGS --extra-cflags="$EXTRA_CFLAGS" --extra-ldflags="$EXTRA_LDFLAGS"
	make clean
	try make -j4
	try make install

	done

	# install
	FFMPEG_LIB="$BUILD_ffmpeg2/build/ffmpeg/armeabi-v7a/lib"
	try cp -a "$FFMPEG_LIB/libavcodec.so" "$LIBS_PATH/libavcodec.so"
	try cp -a "$FFMPEG_LIB/libavdevice.so" "$LIBS_PATH/libavdevice.so"
	try cp -a "$FFMPEG_LIB/libavfilter.so" "$LIBS_PATH/libavfilter.so"
	try cp -a "$FFMPEG_LIB/libavformat.so" "$LIBS_PATH/libavformat.so"
	try cp -a "$FFMPEG_LIB/libavutil.so" "$LIBS_PATH/libavutil.so"
	try cp -a "$FFMPEG_LIB/libswscale.so" "$LIBS_PATH/libswscale.so"
	try cp -a "$FFMPEG_LIB/libswresample.so" "$LIBS_PATH/libswresample.so"
	try cp -a "$FFMPEG_LIB/libpostproc.so" "$LIBS_PATH/libpostproc.so"

	pop_arm
}

function postbuild_ffmpeg2() {
	true
}
