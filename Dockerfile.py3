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

# retry helper script, refs:
# https://github.com/kivy/python-for-android/issues/1306
ENV RETRY="retry -t 3 --"
RUN curl https://raw.githubusercontent.com/kadwanev/retry/1.0.1/retry \
    --output /usr/local/bin/retry && chmod +x /usr/local/bin/retry

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV ANDROID_HOME="${HOME_DIR}/.android"
ENV WORK_DIR="${HOME_DIR}" \
    PATH="${HOME_DIR}/.local/bin:${PATH}"

# install system dependencies
RUN ${RETRY} apt -y install -qq --no-install-recommends \
        python3 virtualenv python3-pip python3-venv \
        wget lbzip2 patch sudo python python-pip \
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

# Install Java and set JAVA_HOME (to accept android's SDK licenses)
RUN ${RETRY} apt -y install -qq --no-install-recommends openjdk-8-jdk \
    && apt -y autoremove && apt -y clean
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}

# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# install cython for python 2 (for python 3 it's inside the venv)
RUN pip2 install --upgrade Cython==0.28.6

WORKDIR ${WORK_DIR}
COPY --chown=user:user . ${WORK_DIR}
RUN mkdir ${ANDROID_HOME} && chown --recursive ${USER} ${ANDROID_HOME}
USER ${USER}

# Download and install android's NDK/SDK
RUN make -f ci/makefiles/android.mk target_os=linux

# install python-for-android from current branch
RUN virtualenv --python=python3 venv \
    && . venv/bin/activate \
    && pip3 install --upgrade Cython==0.28.6 \
    && pip3 install -e .
