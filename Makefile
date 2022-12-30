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
ANDROID_NDK_HOME_LEGACY ?= $(HOME)/.android/android-ndk-legacy
REBUILD_UPDATED_RECIPES_EXTRA_ARGS ?= ''


all: virtualenv

$(VIRTUAL_ENV):
	python3 -m venv $(VIRTUAL_ENV)
	$(PIP) install Cython
	$(PIP) install -e .

virtualenv: $(VIRTUAL_ENV)

# ignores test_pythonpackage.py since it runs for too long
test:
	$(TOX) -- tests/ --ignore tests/test_pythonpackage.py

rebuild_updated_recipes: virtualenv
	. $(ACTIVATE) && \
	ANDROID_SDK_HOME=$(ANDROID_SDK_HOME) ANDROID_NDK_HOME=$(ANDROID_NDK_HOME) \
	$(PYTHON) ci/rebuild_updated_recipes.py $(REBUILD_UPDATED_RECIPES_EXTRA_ARGS)

testapps-with-numpy: virtualenv
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
    python setup.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --requirements libffi,sdl2,pyjnius,kivy,python3,openssl,requests,urllib3,chardet,idna,sqlite3,setuptools,numpy \
    --arch=armeabi-v7a --arch=arm64-v8a --arch=x86_64 --arch=x86 \
	--permission "(name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=18)" --permission "(name=android.permission.INTERNET)"

testapps-with-scipy: virtualenv
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
	export LEGACY_NDK=$(ANDROID_NDK_HOME_LEGACY)  && \
    python setup.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --requirements python3,scipy,kivy \
    --arch=armeabi-v7a --arch=arm64-v8a

testapps-with-numpy-aab: virtualenv
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
    python setup.py aab --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --requirements libffi,sdl2,pyjnius,kivy,python3,openssl,requests,urllib3,chardet,idna,sqlite3,setuptools,numpy \
    --arch=armeabi-v7a --arch=arm64-v8a --arch=x86_64 --arch=x86 --release \
	--permission "(name=android.permission.WRITE_EXTERNAL_STORAGE;maxSdkVersion=18)" --permission "(name=android.permission.INTERNET)"

testapps-service_library-aar: virtualenv
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
    python setup.py aar --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --bootstrap service_library \
    --requirements python3 \
    --arch=arm64-v8a --arch=x86 --release

testapps-webview: virtualenv
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
    python setup.py apk --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --bootstrap webview \
    --requirements sqlite3,libffi,openssl,pyjnius,flask,python3,genericndkbuild \
    --arch=armeabi-v7a --arch=arm64-v8a --arch=x86_64 --arch=x86

testapps-webview-aab: virtualenv
	. $(ACTIVATE) && cd testapps/on_device_unit_tests/ && \
    python setup.py aab --sdk-dir $(ANDROID_SDK_HOME) --ndk-dir $(ANDROID_NDK_HOME) \
    --bootstrap webview \
    --requirements sqlite3,libffi,openssl,pyjnius,flask,python3,genericndkbuild \
    --arch=armeabi-v7a --arch=arm64-v8a --arch=x86_64 --arch=x86 --release

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

docker/run/make/with-artifact/apk/%: docker/build
	docker run --name p4a-latest --env-file=.env $(DOCKER_IMAGE) make $*
	docker cp p4a-latest:/home/user/app/testapps/on_device_unit_tests/bdist_unit_tests_app-debug-1.1.apk ./apks
	docker rm -fv p4a-latest

docker/run/make/with-artifact/aar/%: docker/build
	docker run --name p4a-latest --env-file=.env $(DOCKER_IMAGE) make $*
	docker cp p4a-latest:/home/user/app/testapps/on_device_unit_tests/bdist_unit_tests_app-release-1.1.aar ./aars
	docker rm -fv p4a-latest

docker/run/make/with-artifact/aab/%: docker/build
	docker run --name p4a-latest --env-file=.env $(DOCKER_IMAGE) make $*
	docker cp p4a-latest:/home/user/app/testapps/on_device_unit_tests/bdist_unit_tests_app-release-1.1.aab ./aabs
	docker rm -fv p4a-latest

docker/run/make/rebuild_updated_recipes: docker/build
	docker run --name p4a-latest -e REBUILD_UPDATED_RECIPES_EXTRA_ARGS --env-file=.env $(DOCKER_IMAGE) make rebuild_updated_recipes

docker/run/make/%: docker/build
	docker run --rm --env-file=.env $(DOCKER_IMAGE) make $*

docker/run/shell: docker/build
	docker run --rm --env-file=.env -it $(DOCKER_IMAGE)
