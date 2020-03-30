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

RUN apt -y update -qq > /dev/null && apt -y install -qq --no-install-recommends \
	ca-certificates \
    curl \
    && apt -y autoremove \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

# retry helper script, refs:
# https://github.com/kivy/python-for-android/issues/1306
ENV RETRY="retry -t 3 --"
RUN curl https://raw.githubusercontent.com/kadwanev/retry/1.0.1/retry \
    --output /usr/local/bin/retry && chmod +x /usr/local/bin/retry

ENV USER="user"
ENV HOME_DIR="/home/${USER}"
ENV WORK_DIR="${HOME_DIR}/app" \
    PATH="${HOME_DIR}/.local/bin:${PATH}" \
    ANDROID_HOME="${HOME_DIR}/.android" \
    JAVA_HOME="/usr/lib/jvm/java-8-openjdk-amd64"


# install system dependencies
RUN dpkg --add-architecture i386 \
    && ${RETRY} apt -y update -qq > /dev/null \
    && ${RETRY} apt -y install -qq --no-install-recommends \
    autoconf \
    automake \
    autopoint \
    build-essential \
    ccache \
    cmake \
    gettext \
    git \
    lbzip2 \
    libffi-dev \
    libgtk2.0-0:i386 \
    libidn11:i386 \
    libltdl-dev \
    libncurses5:i386 \
    libpangox-1.0-0:i386 \
    libpangoxft-1.0-0:i386 \
    libstdc++6:i386 \
    libtool \
    openjdk-8-jdk \
    patch \
    pkg-config \
    python \
    python-pip \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    sudo \
    unzip \
    virtualenv \
    wget \
    zip \
    zlib1g-dev \
    zlib1g:i386 \
    && apt -y autoremove \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}

# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# install cython for python 2 (for python 3 it's inside the venv)
RUN pip2 install --upgrade Cython==0.28.6 \
    && rm -rf ~/.cache/

WORKDIR ${WORK_DIR}
RUN mkdir ${ANDROID_HOME} && chown --recursive ${USER} ${HOME_DIR} ${ANDROID_HOME}
USER ${USER}

# Download and install android's NDK/SDK
COPY ci/makefiles/android.mk /tmp/android.mk
RUN make --file /tmp/android.mk target_os=linux \
    && sudo rm /tmp/android.mk

# install python-for-android from current branch
COPY --chown=user:user Makefile README.md setup.py pythonforandroid/__init__.py ${WORK_DIR}/
RUN mkdir pythonforandroid \
    && mv __init__.py pythonforandroid/ \
    && make virtualenv \
    && rm -rf ~/.cache/

COPY --chown=user:user . ${WORK_DIR}
