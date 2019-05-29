# Dockerfile with:
#   - Android build environment
#   - python-for-android dependencies
#
# Build with:
#     docker build --tag=p4a --file Dockerfile.py3 .
#
# Run with:
#     docker run -it --rm p4a /bin/sh -c '. venv/bin/activate && p4a apk --help'
#
# Or for interactive shell:
#     docker run -it --rm p4a
#
# Note:
#     Use 'docker run' without '--rm' flag for keeping the container and use
#     'docker commit <container hash> <new image>' to extend the original image

FROM ubuntu:18.04

ENV ANDROID_HOME="/opt/android"

# configure locale
RUN apt update -qq > /dev/null && apt install -qq --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

RUN apt -y update -qq \
    && apt -y install -qq --no-install-recommends curl unzip ca-certificates \
    && apt -y autoremove

RUN apt-get update && apt-get install --no-install-recommends --yes \
    autoconf \
    automake \
    build-essential \
    ca-certificates \
    cmake \
    dh-systemd \
    fakeroot \
    git \
    libswscale-dev \
    libopenexr-dev \
    lintian \
    openjdk-8-jdk \
    software-properties-common \
    unzip \
    yasm \
    wget \
  && apt-get clean && rm -rf /var/tmp/*

# retry helper script, refs:
# https://github.com/kivy/python-for-android/issues/1306
ENV RETRY="retry -t 3 --"
RUN curl https://raw.githubusercontent.com/kadwanev/retry/1.0.1/retry \
    --output /usr/local/bin/retry && chmod +x /usr/local/bin/retry

ENV ANDROID_NDK_HOME="${ANDROID_HOME}/android-ndk"
ENV ANDROID_NDK_VERSION="17c"
ENV ANDROID_NDK_HOME_V="${ANDROID_NDK_HOME}-r${ANDROID_NDK_VERSION}"

# get the latest version from https://developer.android.com/ndk/downloads/index.html
ENV ANDROID_NDK_ARCHIVE="android-ndk-r${ANDROID_NDK_VERSION}-linux-x86_64.zip"
ENV ANDROID_NDK_DL_URL="https://dl.google.com/android/repository/${ANDROID_NDK_ARCHIVE}"

# download and install Android NDK
RUN ${RETRY} curl --location --progress-bar --insecure \
        "${ANDROID_NDK_DL_URL}" \
        --output "${ANDROID_NDK_ARCHIVE}" \
    && mkdir --parents "${ANDROID_NDK_HOME_V}" \
    && unzip -q "${ANDROID_NDK_ARCHIVE}" -d "${ANDROID_HOME}" \
    && ln -sfn "${ANDROID_NDK_HOME_V}" "${ANDROID_NDK_HOME}" \
    && rm -rf "${ANDROID_NDK_ARCHIVE}"


ENV ANDROID_SDK_HOME="${ANDROID_HOME}/android-sdk"

# get the latest version from https://developer.android.com/studio/index.html
ENV ANDROID_SDK_TOOLS_VERSION="3859397"
ENV ANDROID_SDK_BUILD_TOOLS_VERSION="26.0.2"
ENV ANDROID_SDK_TOOLS_ARCHIVE="sdk-tools-linux-${ANDROID_SDK_TOOLS_VERSION}.zip"
ENV ANDROID_SDK_TOOLS_DL_URL="https://dl.google.com/android/repository/${ANDROID_SDK_TOOLS_ARCHIVE}"

# download and install Android SDK
RUN ${RETRY} curl --location --progress-bar --insecure \
        "${ANDROID_SDK_TOOLS_DL_URL}" \
        --output "${ANDROID_SDK_TOOLS_ARCHIVE}" \
    && mkdir --parents "${ANDROID_SDK_HOME}" \
    && unzip -q "${ANDROID_SDK_TOOLS_ARCHIVE}" -d "${ANDROID_SDK_HOME}" \
    && rm -rf "${ANDROID_SDK_TOOLS_ARCHIVE}"

# update Android SDK, install Android API, Build Tools...
RUN mkdir --parents "${ANDROID_SDK_HOME}/.android/" \
    && echo '### User Sources for Android SDK Manager' \
        > "${ANDROID_SDK_HOME}/.android/repositories.cfg"

# accept Android licenses (JDK necessary!)
RUN ${RETRY} apt -y install -qq --no-install-recommends openjdk-8-jdk \
    && apt -y autoremove
RUN yes | "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "build-tools;${ANDROID_SDK_BUILD_TOOLS_VERSION}" > /dev/null

# download platforms, API, build tools
RUN "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "platforms;android-19" && \
    "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "platforms;android-27" && \
    "${ANDROID_SDK_HOME}/tools/bin/sdkmanager" "build-tools;${ANDROID_SDK_BUILD_TOOLS_VERSION}" && \
    chmod +x "${ANDROID_SDK_HOME}/tools/bin/avdmanager"

ENV NDK_ROOT ${ANDROID_NDK_HOME}
ENV ANDROID_NATIVE_API_LEVEL ${ANDROIDAPI}
ENV ANDROID_ABI "armeabi-v7a"
ENV TARGET_ANDROID_ABI $ANDROID_ABI

ENV TOOLCHAIN arm-linux-androideabi-4.9
ENV TOOLCHAIN_DIR ${ANDROID_NDK_HOME}/toolchains/${TOOLCHAIN}

# ENV CMAKE_TOOLCHAIN_FILE ${PROJECT_DIR}/android-cmake/android.toolchain.cmake
# ENV CMAKE_TOOLCHAIN_FILE /opt/tools/cmake/3.6.4111459/android.toolchain.cmake
ENV CMAKE_TOOLCHAIN_FILE ${ANDROID_NDK_HOME}/build/cmake/android.toolchain.cmake


# Host libraries
ENV PROJECT_DIR /opt/src
ENV INSTALL_DIR /opt/install
ENV N_JOBS ${N_JOBS:-4}
ENV OS linux
ENV ARCH x86_64

# golang
ENV GOLANG_VERSION 1.12.4
RUN curl -Lo /tmp/go.tar.gz \
    https://golang.org/dl/go${GOLANG_VERSION}.linux-amd64.tar.gz \
  && tar -C /usr/local -xzf /tmp/go.tar.gz \
  && rm /tmp/go.tar.gz
ENV PATH "/usr/local/go/bin:${PATH}"
RUN go version


# gFlags
ENV GFLAGS_VERSION v2.2.1
ENV BUILD_DIR /opt/build/gflags
RUN mkdir -p ${PROJECT_DIR}/gflags \
  && curl -Lo /tmp/gflags.tar.gz \
      https://github.com/gflags/gflags/archive/${GFLAGS_VERSION}.tar.gz \
  && tar -xzvf /tmp/gflags.tar.gz -C ${PROJECT_DIR}/gflags --strip-components 1 \
  && rm /tmp/gflags.tar.gz \
  && mkdir -p "${BUILD_DIR}" && cd "${BUILD_DIR}" \
  && cmake -DCMAKE_TOOLCHAIN_FILE="${CMAKE_TOOLCHAIN_FILE}" \
      -DANDROID_NDK="${NDK_ROOT}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DANDROID_ABI="${ANDROID_ABI}" \
      -DANDROID_NATIVE_API_LEVEL=21 \
      -DANDROID_STL=c++_static \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
      -DCMAKE_FIND_ROOT_PATH="${INSTALL_DIR}" \
      "${PROJECT_DIR}/gflags" \
  && cmake --build . --target install/strip -- -j"${N_JOBS}" \
  && rm -rf "${BUILD_DIR}"


# gLog
ENV GLOG_VERSION v0.3.5
ENV BUILD_DIR /opt/build/glog
# COPY caffe-android-lib/glog ${PROJECT_DIR}/glog
RUN mkdir -p ${PROJECT_DIR}/glog \
  && curl -Lo /tmp/glog.tar.gz \
      https://github.com/google/glog/archive/${GLOG_VERSION}.tar.gz \
  && tar -xzvf /tmp/glog.tar.gz -C ${PROJECT_DIR}/glog --strip-components 1 \
  && rm /tmp/glog.tar.gz \
  && mkdir -p "${BUILD_DIR}" && cd "${BUILD_DIR}" \
  && cmake -DCMAKE_TOOLCHAIN_FILE="${CMAKE_TOOLCHAIN_FILE}" \
      -DANDROID_NDK="${NDK_ROOT}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DANDROID_ABI="${ANDROID_ABI}" \
      -DANDROID_NATIVE_API_LEVEL=21 \
      -DANDROID_STL=c++_static \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
      -DCMAKE_FIND_ROOT_PATH="${INSTALL_DIR}" \
      -DBUILD_TESTING=OFF \
      "${PROJECT_DIR}/glog" \
  && cmake --build . --target install/strip  -- -j"${N_JOBS}" \
  && rm -rf "${BUILD_DIR}"


# gRPC
ENV GRPC_ROOT ${PROJECT_DIR}/grpc
ENV GRPC_RELEASE_TAG v1.20.1
# ENV BUILD_DIR /opt/build/grpc
RUN git clone -b ${GRPC_RELEASE_TAG} https://github.com/grpc/grpc ${GRPC_ROOT} \
  && cd ${GRPC_ROOT} \
  && git submodule update --init

# Host Protobuf
# This is needed because we will run "protoc" when building other dependencies.
# The target "protoc" executable doesn't work because of the platform mismatch
ENV BUILD_DIR /opt/build/protobuf_host
RUN mkdir -p "${BUILD_DIR}" && cd "${BUILD_DIR}" \
  && cmake \
      -Dprotobuf_BUILD_TESTS=OFF \
      ${PROJECT_DIR}/grpc/third_party/protobuf/cmake \
  && cmake --build . --target install/strip -- -j"${N_JOBS}" \
  && rm -rf "${BUILD_DIR}"

# RUN apt-get install --yes zlib1g-dev libc-ares-dev libssl1.0-dev

# GRPC HOST #
ENV BUILD_DIR /opt/build/grpc-host
RUN mkdir -p ${BUILD_DIR} && cd ${BUILD_DIR} \
  && cmake \
      -DCMAKE_BUILD_TYPE=Release \
      -DProtobuf_PROTOC_EXECUTABLE=/usr/local/bin/protoc \
      -DgRPC_INSTALL=ON \
      -DgRPC_BUILD_TESTS=OFF \
      ${GRPC_ROOT} \
  && cmake --build . --target install/strip -- -j"${N_JOBS}"
  # We don't remove this because some executables are not installed (to fix)
  # && rm -rf "${BUILD_DIR}"

# Android ZLib
# To understand why submodules zlib, cares and protobuf are being built and
# removed from grpc tree check: https://github.com/grpc/grpc/issues/13841
ENV BUILD_DIR /opt/build/zlib
RUN mkdir -p "${BUILD_DIR}" && cd "${BUILD_DIR}" \
  && cmake -DCMAKE_TOOLCHAIN_FILE="${CMAKE_TOOLCHAIN_FILE}" \
      -DANDROID_NDK="${NDK_ROOT}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DANDROID_ABI="${ANDROID_ABI}" \
      -DANDROID_NATIVE_API_LEVEL=21 \
      -DANDROID_STL=c++_static \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
      -DCMAKE_FIND_ROOT_PATH="${INSTALL_DIR}" \
      ${PROJECT_DIR}/grpc/third_party/zlib \
  && cmake --build . --target install/strip -- -j"${N_JOBS}" \
  && rm -rf "${BUILD_DIR}" \
  # Wipe out to prevent influencing the grpc build
  && rm -rf ${PROJECT_DIR}/grpc/third_party/zlib

# Android c-ares
ENV BUILD_DIR /opt/build/cares
RUN mkdir -p "${BUILD_DIR}" && cd "${BUILD_DIR}" \
  && cmake -DCMAKE_TOOLCHAIN_FILE="${CMAKE_TOOLCHAIN_FILE}" \
      -DANDROID_NDK="${NDK_ROOT}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DANDROID_ABI="${ANDROID_ABI}" \
      -DANDROID_NATIVE_API_LEVEL=21 \
      -DANDROID_STL=c++_static \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
      -DCMAKE_FIND_ROOT_PATH="${INSTALL_DIR}" \
      ${PROJECT_DIR}/grpc/third_party/cares/cares \
  && cmake --build . --target install/strip -- -j"${N_JOBS}" \
  && rm -rf "${BUILD_DIR}" \
  # Wipe out to prevent influencing the grpc build
  && rm -rf ${PROJECT_DIR}/grpc/third_party/cares

ENV OPENSSL_ROOT ${PROJECT_DIR}/openssl
RUN mkdir -p ${OPENSSL_ROOT} \
  && curl -Lo /tmp/openssl.tar.gz \
      https://github.com/openssl/openssl/archive/OpenSSL_1_1_1b.tar.gz \
  && tar -xzvf /tmp/openssl.tar.gz -C ${OPENSSL_ROOT} --strip-components 1 \
  && cd ${OPENSSL_ROOT} \
  && PATH="${TOOLCHAIN_DIR}/prebuilt/linux-x86_64/bin/:${PATH}" ./Configure android-arm -D__ANDROID_API__=21 \
  && PATH="${TOOLCHAIN_DIR}/prebuilt/linux-x86_64/bin/:${PATH}" make install

# Android Protobuf
ENV BUILD_DIR /opt/build/protobuf
RUN mkdir -p "${BUILD_DIR}" && cd "${BUILD_DIR}" \
  && cmake -DCMAKE_TOOLCHAIN_FILE="${CMAKE_TOOLCHAIN_FILE}" \
      -DANDROID_NDK="${NDK_ROOT}" \
      -DCMAKE_BUILD_TYPE=Release \
      -DANDROID_ABI="${ANDROID_ABI}" \
      -DANDROID_NATIVE_API_LEVEL=21 \
      -DCMAKE_CXX_STANDARD=11 \
      -DANDROID_STL=c++_static \
      -DCMAKE_INSTALL_PREFIX="${INSTALL_DIR}" \
      -DCMAKE_FIND_ROOT_PATH="${INSTALL_DIR}" \
      -Dprotobuf_BUILD_TESTS=OFF \
      -DCMAKE_EXE_LINKER_FLAGS="-llog" \
      #-Dprotobuf_BUILD_PROTOC_BINARIES=OFF \
      ${PROJECT_DIR}/grpc/third_party/protobuf/cmake \
  && cmake --build . --target install/strip -- -j"${N_JOBS}" \
  && rm -rf "${BUILD_DIR}" \
  # Wipe out to prevent influencing the grpc build
  && rm -rf ${PROJECT_DIR}/grpc/third_party/protobuf \
  # bug: link symbolics missed for GRPC compiling
  && ln -sf /opt/android/android-ndk/platforms/android-21/arch-arm/usr/lib/libc.so /opt/android/android-ndk/platforms/android-21/arch-arm/usr/lib/libnsl.so \
  && ln -sf /opt/android/android-ndk/platforms/android-21/arch-arm/usr/lib/libc.so /opt/android/android-ndk/platforms/android-21/arch-arm/usr/lib/librt.so

# Python and user packages

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV WORK_DIR="${HOME_DIR}" \
    PATH="${HOME_DIR}/.local/bin:${PATH}"

# install system dependencies
RUN ${RETRY} apt -y install -qq --no-install-recommends \
        python3 virtualenv python3-pip python3-venv \
        wget lbzip2 patch sudo \
    && apt -y autoremove

# build dependencies
# https://buildozer.readthedocs.io/en/latest/installation.html#android-on-ubuntu-16-04-64bit
RUN dpkg --add-architecture i386 \
    && ${RETRY} apt -y update -qq \
    && ${RETRY} apt -y install -qq --no-install-recommends \
        build-essential ccache git python3 python3-dev \
        libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 \
        libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 \
        zip zlib1g-dev zlib1g:i386 \
    && apt -y autoremove

# specific recipes dependencies (e.g. libffi requires autoreconf binary)
RUN ${RETRY} apt -y install -qq --no-install-recommends \
        libffi-dev autoconf automake cmake gettext libltdl-dev libtool pkg-config \
    && apt -y autoremove \
    && apt -y clean

# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}

# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers


RUN pip3 install --upgrade cython==0.28.6

WORKDIR ${WORK_DIR}
COPY --chown=user:user . ${WORK_DIR}
RUN chown --recursive ${USER} ${ANDROID_SDK_HOME}
USER ${USER}

# install python-for-android from current branch
RUN virtualenv --python=python3 venv \
    && . venv/bin/activate \
    && pip3 install -e .

