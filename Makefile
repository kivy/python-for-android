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
ANDROID_SDK_HOME ?= $(HOME)/.android/android-sdk
ANDROID_NDK_HOME ?= $(HOME)/.android/android-ndk
DOCKER_IMAGE=kivy/python-for-android
# tag to latest only on merge to develop
DOCKER_TAG=latest
ifdef TRAVIS_PULL_REQUEST
ifneq ($(TRAVIS_PULL_REQUEST), false)
	DOCKER_TAG=pr-$(TRAVIS_PULL_REQUEST)
else ifneq ($(TRAVIS_BRANCH), develop)
	DOCKER_TAG=branch-$(subst /,-,$(TRAVIS_BRANCH)) # slash is an invalid docker tag character
endif
endif


all: virtualenv

$(VIRTUAL_ENV):
	virtualenv --python=$(PYTHON_WITH_VERSION) $(VIRTUAL_ENV)
	$(PIP) install Cython==0.28.6
	$(PIP) install -e .

virtualenv: $(VIRTUAL_ENV)

# ignores test_pythonpackage.py since it runs for too long
test:
	$(TOX) -- tests/ --ignore tests/test_pythonpackage.py
	@if test -n "$$CI"; then .tox/py$(PYTHON_MAJOR_MINOR)/bin/coveralls; fi; \

rebuild_updated_recipes: virtualenv
	$(PYTHON) ci/rebuild_updated_recipes.py

testapps/python2/armeabi-v7a: virtualenv
	. $(ACTIVATE) && cd testapps/ && \
    python setup_testapp_python2_sqlite_openssl.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --requirements sdl2,pyjnius,kivy,python2,openssl,requests,sqlite3,setuptools,numpy

testapps/python3/arm64-v8a: virtualenv
	. $(ACTIVATE) && cd testapps/ && \
    python setup_testapp_python3_sqlite_openssl.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --arch=arm64-v8a

testapps/python3/armeabi-v7a: virtualenv
	. $(ACTIVATE) && cd testapps/ && \
    python setup_testapp_python3_sqlite_openssl.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --requirements libffi,sdl2,pyjnius,kivy,python3,openssl,requests,sqlite3,setuptools \
    --arch=armeabi-v7a

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "*.egg-info" -exec rm -r {} +

clean/all: clean
	rm -rf $(VIRTUAL_ENV) .tox/

docker/pull:
	docker pull $(DOCKER_IMAGE):$(DOCKER_TAG) || docker pull $(DOCKER_IMAGE):latest || true

docker/build:
	docker build --cache-from=$(DOCKER_IMAGE):$(DOCKER_TAG) --tag=$(DOCKER_IMAGE):$(DOCKER_TAG) --file=Dockerfile.py3 .

docker/login:
	docker login --username $(DOCKER_USERNAME) --password $(DOCKER_PASSWORD) || true

docker/push: docker/login
	docker push $(DOCKER_IMAGE) || true

docker/run/test: docker/build
	docker run --rm --env-file=.env $(DOCKER_IMAGE) 'make test'

docker/run/command: docker/build
	docker run --rm --env-file=.env $(DOCKER_IMAGE) /bin/sh -c "$(COMMAND)"

docker/run/make/%: docker/build
	docker run --rm --env-file=.env $(DOCKER_IMAGE):$(DOCKER_TAG) make $*

docker/run/shell: docker/build
	docker run --rm --env-file=.env -it $(DOCKER_IMAGE)
