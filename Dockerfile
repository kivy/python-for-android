# Dockerfile with:
# 	- Android build environment
# 	- python-for-android dependencies
# Build with:
# docker build --tag=p4a .
# Run with:
# docker run p4a /bin/sh -c '. venv/bin/activate && p4a apk --help'
# Or for interactive shell:
# docker run -it --rm p4a
#
# TODO:
#	- delete archives to keep small the container small
#	- setup caching (for apt, pip, ndk, sdk and p4a recipes downloads)
FROM ubuntu:16.04


# get the latest version from https://developer.android.com/ndk/downloads/index.html
ENV ANDROID_NDK_VERSION="16b"
# get the latest version from https://developer.android.com/studio/index.html
ENV ANDROID_SDK_TOOLS_VERSION="3859397"

ENV ANDROID_HOME="/opt/android"
ENV ANDROID_NDK_HOME="${ANDROID_HOME}/android-ndk" \
	ANDROID_SDK_HOME="${ANDROID_HOME}/android-sdk"
ENV ANDROID_NDK_HOME_V="${ANDROID_NDK_HOME}-r${ANDROID_NDK_VERSION}"
ENV ANDROID_NDK_ARCHIVE="android-ndk-r${ANDROID_NDK_VERSION}-linux-x86_64.zip" \
	ANDROID_SDK_TOOLS_ARCHIVE="sdk-tools-linux-${ANDROID_SDK_TOOLS_VERSION}.zip"
ENV ANDROID_NDK_DL_URL="https://dl.google.com/android/repository/${ANDROID_NDK_ARCHIVE}" \
	ANDROID_SDK_TOOLS_DL_URL="https://dl.google.com/android/repository/${ANDROID_SDK_TOOLS_ARCHIVE}"

# install system dependencies
RUN apt update -qq && apt install -qq --yes --no-install-recommends \
	python virtualenv python-pip wget curl lbzip2 patch

# build dependencies
# https://buildozer.readthedocs.io/en/latest/installation.html#android-on-ubuntu-16-04-64bit
RUN dpkg --add-architecture i386 &&  apt update -qq && apt install -qq --yes --no-install-recommends \
	build-essential ccache git libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 \
	libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 python2.7 python2.7-dev \
	openjdk-8-jdk unzip zlib1g-dev zlib1g:i386
RUN	pip install --quiet --upgrade cython==0.21

# download and install Android NDK
RUN curl --progress-bar "${ANDROID_NDK_DL_URL}" --output "${ANDROID_NDK_ARCHIVE}" && \
    mkdir --parents "${ANDROID_NDK_HOME_V}" && \
    unzip -q "${ANDROID_NDK_ARCHIVE}" -d "${ANDROID_HOME}" && \
	ln -sfn "${ANDROID_NDK_HOME_V}" "${ANDROID_NDK_HOME}"

# download and install Android SDK
RUN curl --progress-bar "${ANDROID_SDK_TOOLS_DL_URL}" --output "${ANDROID_SDK_TOOLS_ARCHIVE}" && \
    mkdir --parents "${ANDROID_SDK_HOME}" && \
    unzip -q "${ANDROID_SDK_TOOLS_ARCHIVE}" -d "${ANDROID_SDK_HOME}"

# update Android SDK, install Android API, Build Tools...
RUN mkdir --parents "${ANDROID_SDK_HOME}/.android/" && \
	echo '### User Sources for Android SDK Manager' > "${ANDROID_SDK_HOME}/.android/repositories.cfg"
RUN yes | "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" --licenses
RUN "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "platforms;android-19"
RUN "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "build-tools;26.0.2"

# install python-for-android from current branch
WORKDIR /app
COPY . /app
RUN virtualenv --python=python venv && . venv/bin/activate && pip install --quiet -e .
