VIRTUAL_ENV ?= venv
PIP=$(VIRTUAL_ENV)/bin/pip
TOX=`which tox`
ACTIVATE=$(VIRTUAL_ENV)/bin/activate
PYTHON=$(VIRTUAL_ENV)/bin/python
FLAKE8=$(VIRTUAL_ENV)/bin/flake8
PYTEST=$(VIRTUAL_ENV)/bin/pytest
SOURCES=src/ tests/
PYTHON_MAJOR_VERSION=3
PYTHON_MINOR_VERSION=6
PYTHON_VERSION=$(PYTHON_MAJOR_VERSION).$(PYTHON_MINOR_VERSION)
PYTHON_MAJOR_MINOR=$(PYTHON_MAJOR_VERSION)$(PYTHON_MINOR_VERSION)
PYTHON_WITH_VERSION=python$(PYTHON_VERSION)
DOCKER_IMAGE=kivy/python-for-android
ANDROID_SDK_HOME ?= $(HOME)/.android/android-sdk
ANDROID_NDK_HOME ?= $(HOME)/.android/android-ndk


all: virtualenv

$(VIRTUAL_ENV):
	python3 -m venv $(VIRTUAL_ENV)
	$(PIP) install Cython==0.29.19
	$(PIP) install -e .

virtualenv: $(VIRTUAL_ENV)

# ignores test_pythonpackage.py since it runs for too long
test:
	$(TOX) -- tests/ --ignore tests/test_pythonpackage.py

rebuild_updated_recipes: virtualenv
	. $(ACTIVATE) && \
	ANDROID_SDK_HOME=$(ANDROID_SDK_HOME) ANDROID_NDK_HOME=$(ANDROID_NDK_HOME) \
	$(PYTHON) ci/rebuild_updated_recipes.py

testapps-with-numpy/%: virtualenv
	$(eval $@_APP_ARCH := $(shell basename $*))
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
    python setup.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --requirements libffi,sdl2,pyjnius,kivy,python3,openssl,requests,urllib3,chardet,idna,sqlite3,setuptools,numpy \
    --arch=$($@_APP_ARCH)

testapps/%: virtualenv
	$(eval $@_APP_ARCH := $(shell basename $*))
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
    python setup.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --arch=$($@_APP_ARCH)

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

clean/all: clean
	rm -rf $(VIRTUAL_ENV) .tox/

docker/pull:
	docker pull $(DOCKER_IMAGE):latest || true

docker/build:
	docker build --cache-from=$(DOCKER_IMAGE) --tag=$(DOCKER_IMAGE) .

docker/push:
	docker push $(DOCKER_IMAGE)

docker/run/test: docker/build
	docker run --rm --env-file=.env $(DOCKER_IMAGE) 'make test'

docker/run/command: docker/build
	docker run --rm --env-file=.env $(DOCKER_IMAGE) /bin/sh -c "$(COMMAND)"

docker/run/make/%: docker/build
	docker run --rm --env-file=.env $(DOCKER_IMAGE) make $*

docker/run/make/with-artifact/%: docker/build
	$(eval $@_APP_ARCH := $(shell basename $*))
	docker run --name p4a-latest --env-file=.env $(DOCKER_IMAGE) make $*
	docker cp p4a-latest:/home/user/app/testapps/on_device_unit_tests/bdist_unit_tests_app__$($@_APP_ARCH)-debug-1.1-.apk ./apks
	docker rm -fv p4a-latest

docker/run/shell: docker/build
	docker run --rm --env-file=.env -it $(DOCKER_IMAGE)
