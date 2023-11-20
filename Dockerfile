# Dockerfile with:
#   - Android build environment
#   - python-for-android dependencies
#
# Build with:
#     docker build --tag=p4a --file Dockerfile .
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

# If platform is not specified, by default the target platform of the build request is used.
# This is not what we want, as Google doesn't provide a linux/arm64 compatible NDK.
# See: https://docs.docker.com/engine/reference/builder/#from
FROM --platform=linux/amd64 ubuntu:22.04

# configure locale
RUN apt -y update -qq > /dev/null \
    && DEBIAN_FRONTEND=noninteractive apt install -qq --yes --no-install-recommends \
    locales && \
    locale-gen en_US.UTF-8
ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US.UTF-8" \
    LC_ALL="en_US.UTF-8"

RUN apt -y update -qq > /dev/null \
    && DEBIAN_FRONTEND=noninteractive apt install -qq --yes --no-install-recommends \
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
    JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"


# install system dependencies
RUN ${RETRY} apt -y update -qq > /dev/null \
    && ${RETRY} DEBIAN_FRONTEND=noninteractive apt install -qq --yes --no-install-recommends \
        ant \
        autoconf \
        automake \
        ccache \
        cmake \
        g++ \
        gcc \
        git \
        lbzip2 \
        libffi-dev \
        libltdl-dev \
        libtool \
        libssl-dev \
        make \
        openjdk-17-jdk \
        patch \
        pkg-config \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        sudo \
        unzip \
        wget \
        zip \
    && apt -y autoremove \
    && apt -y clean \
    && rm -rf /var/lib/apt/lists/*

# prepare non root env
RUN useradd --create-home --shell /bin/bash ${USER}

# with sudo access and no password
RUN usermod -append --groups sudo ${USER}
RUN echo "%sudo ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

WORKDIR ${WORK_DIR}
RUN mkdir ${ANDROID_HOME} && chown --recursive ${USER} ${HOME_DIR} ${ANDROID_HOME}
USER ${USER}

# Download and install android's NDK/SDK
COPY --chown=user:user ci/makefiles/android.mk /tmp/android.mk
RUN make --file /tmp/android.mk \
    && sudo rm /tmp/android.mk

# install python-for-android from current branch
COPY --chown=user:user Makefile README.md setup.py pythonforandroid/__init__.py ${WORK_DIR}/
RUN mkdir pythonforandroid \
    && mv __init__.py pythonforandroid/ \
    && make virtualenv \
    && rm -rf ~/.cache/

COPY --chown=user:user . ${WORK_DIR}
