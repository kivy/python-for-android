# Downloads and installs the Android SDK depending on supplied platform: darwin or linux

# Those android NDK/SDK variables can be override when running the file
ANDROID_NDK_VERSION ?= 23b
ANDROID_SDK_TOOLS_VERSION ?= 6514223
ANDROID_SDK_BUILD_TOOLS_VERSION ?= 29.0.3
ANDROID_HOME ?= $(HOME)/.android
ANDROID_API_LEVEL ?= 27

# per OS dictionary-like
UNAME_S := $(shell uname -s)
TARGET_OS_Linux = linux
TARGET_OS_ALIAS_Linux = $(TARGET_OS_Linux)
TARGET_OS_Darwin = darwin
TARGET_OS_ALIAS_Darwin = mac
TARGET_OS = $(TARGET_OS_$(UNAME_S))
TARGET_OS_ALIAS = $(TARGET_OS_ALIAS_$(UNAME_S))

ANDROID_SDK_HOME=$(ANDROID_HOME)/android-sdk
ANDROID_SDK_TOOLS_ARCHIVE=commandlinetools-$(TARGET_OS_ALIAS)-$(ANDROID_SDK_TOOLS_VERSION)_latest.zip
ANDROID_SDK_TOOLS_DL_URL=https://dl.google.com/android/repository/$(ANDROID_SDK_TOOLS_ARCHIVE)

ANDROID_NDK_HOME=$(ANDROID_HOME)/android-ndk
ANDROID_NDK_FOLDER=$(ANDROID_HOME)/android-ndk-r$(ANDROID_NDK_VERSION)
ANDROID_NDK_ARCHIVE=android-ndk-r$(ANDROID_NDK_VERSION)-$(TARGET_OS).zip
ANDROID_NDK_DL_URL=https://dl.google.com/android/repository/$(ANDROID_NDK_ARCHIVE)

$(info Target install OS is          : $(target_os))
$(info Android SDK home is           : $(ANDROID_SDK_HOME))
$(info Android NDK home is           : $(ANDROID_NDK_HOME))
$(info Android SDK download url is   : $(ANDROID_SDK_TOOLS_DL_URL))
$(info Android NDK download url is   : $(ANDROID_NDK_DL_URL))
$(info Android API level is          : $(ANDROID_API_LEVEL))
$(info Android NDK version is        : $(ANDROID_NDK_VERSION))
$(info JAVA_HOME is                  : $(JAVA_HOME))

all: install_sdk install_ndk

install_sdk: download_android_sdk extract_android_sdk update_android_sdk

install_ndk: download_android_ndk extract_android_ndk

download_android_sdk:
	curl --location --progress-bar --continue-at - \
	$(ANDROID_SDK_TOOLS_DL_URL) --output $(ANDROID_SDK_TOOLS_ARCHIVE)

download_android_ndk:
	curl --location --progress-bar --continue-at - \
	$(ANDROID_NDK_DL_URL) --output $(ANDROID_NDK_ARCHIVE)

# Extract android SDK and remove the compressed file
extract_android_sdk:
	mkdir -p $(ANDROID_SDK_HOME) \
	&& unzip -q $(ANDROID_SDK_TOOLS_ARCHIVE) -d $(ANDROID_SDK_HOME) \
	&& rm -f $(ANDROID_SDK_TOOLS_ARCHIVE)


# Extract android NDK and remove the compressed file
extract_android_ndk:
	mkdir -p $(ANDROID_NDK_FOLDER) \
	&& unzip -q $(ANDROID_NDK_ARCHIVE) -d $(ANDROID_HOME) \
	&& mv $(ANDROID_NDK_FOLDER) $(ANDROID_NDK_HOME) \
	&& rm -f $(ANDROID_NDK_ARCHIVE)

# updates Android SDK, install Android API, Build Tools and accept licenses
update_android_sdk:
	touch $(ANDROID_HOME)/repositories.cfg
	yes | $(ANDROID_SDK_HOME)/tools/bin/sdkmanager --sdk_root=$(ANDROID_SDK_HOME) --licenses > /dev/null
	$(ANDROID_SDK_HOME)/tools/bin/sdkmanager --sdk_root=$(ANDROID_SDK_HOME) "build-tools;$(ANDROID_SDK_BUILD_TOOLS_VERSION)" > /dev/null
	$(ANDROID_SDK_HOME)/tools/bin/sdkmanager --sdk_root=$(ANDROID_SDK_HOME) "platforms;android-$(ANDROID_API_LEVEL)" > /dev/null
	# Set avdmanager permissions (executable)
	chmod +x $(ANDROID_SDK_HOME)/tools/bin/avdmanager
