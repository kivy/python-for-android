# Downloads and installs the Android SDK depending on supplied platform: darwin or linux

# Those android NDK/SDK variables can be override when running the file
ANDROID_NDK_VERSION ?= 25b
ANDROID_NDK_VERSION_LEGACY ?= 21e
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

ANDROID_NDK_HOME_LEGACY=$(ANDROID_HOME)/android-ndk-legacy
ANDROID_NDK_FOLDER_LEGACY=$(ANDROID_HOME)/android-ndk-r$(ANDROID_NDK_VERSION_LEGACY)
ANDROID_NDK_ARCHIVE_LEGACY=android-ndk-r$(ANDROID_NDK_VERSION_LEGACY)-$(TARGET_OS)-x86_64.zip

ANDROID_NDK_GFORTRAN_ARCHIVE_ARM64=gcc-arm64-linux-x86_64.tar.bz2
ANDROID_NDK_GFORTRAN_ARCHIVE_ARM=gcc-arm-linux-x86_64.tar.bz2


ANDROID_NDK_DL_URL=https://dl.google.com/android/repository/$(ANDROID_NDK_ARCHIVE)
ANDROID_NDK_DL_URL_LEGACY=https://dl.google.com/android/repository/$(ANDROID_NDK_ARCHIVE_LEGACY)

$(info Target install OS is          : $(target_os))
$(info Android SDK home is           : $(ANDROID_SDK_HOME))
$(info Android NDK home is           : $(ANDROID_NDK_HOME))
$(info Android NDK Legacy  home is   : $(ANDROID_NDK_HOME_LEGACY))
$(info Android SDK download url is   : $(ANDROID_SDK_TOOLS_DL_URL))
$(info Android NDK download url is   : $(ANDROID_NDK_DL_URL))
$(info Android API level is          : $(ANDROID_API_LEVEL))
$(info Android NDK version is        : $(ANDROID_NDK_VERSION))
$(info Android NDK Legacy version is : $(ANDROID_NDK_VERSION_LEGACY))
$(info JAVA_HOME is                  : $(JAVA_HOME))

all: install_sdk install_ndk

install_sdk: download_android_sdk extract_android_sdk update_android_sdk

install_ndk: download_android_ndk download_android_ndk_legacy download_android_ndk_gfortran extract_android_ndk extract_android_ndk_legacy extract_android_ndk_gfortran

download_android_sdk:
	curl --location --progress-bar --continue-at - \
	$(ANDROID_SDK_TOOLS_DL_URL) --output $(ANDROID_SDK_TOOLS_ARCHIVE)

download_android_ndk:
	curl --location --progress-bar --continue-at - \
	$(ANDROID_NDK_DL_URL) --output $(ANDROID_NDK_ARCHIVE)

download_android_ndk_legacy:
	curl --location --progress-bar --continue-at - \
	$(ANDROID_NDK_DL_URL_LEGACY) --output $(ANDROID_NDK_ARCHIVE_LEGACY)

download_android_ndk_gfortran:
	curl --location --progress-bar --continue-at - \
	https://github.com/mzakharo/android-gfortran/releases/download/r$(ANDROID_NDK_VERSION_LEGACY)/$(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM64) --output $(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM64)
	curl --location --progress-bar --continue-at - \
	https://github.com/mzakharo/android-gfortran/releases/download/r$(ANDROID_NDK_VERSION_LEGACY)/$(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM)  --output $(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM)


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

extract_android_ndk_legacy:
	mkdir -p $(ANDROID_NDK_FOLDER_LEGACY) \
	&& unzip -q $(ANDROID_NDK_ARCHIVE_LEGACY) -d $(ANDROID_HOME) \
	&& mv $(ANDROID_NDK_FOLDER_LEGACY) $(ANDROID_NDK_HOME_LEGACY) \
	&& rm -f $(ANDROID_NDK_ARCHIVE_LEGACY)

extract_android_ndk_gfortran:
	rm -rf $(ANDROID_NDK_HOME_LEGACY)/toolchains/aarch64-linux-android-4.9/prebuilt/linux-x86_64/ \
	&& mkdir  $(ANDROID_NDK_HOME_LEGACY)/toolchains/aarch64-linux-android-4.9/prebuilt/linux-x86_64/ \
	&& tar -xf $(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM64) -C $(ANDROID_NDK_HOME_LEGACY)/toolchains/aarch64-linux-android-4.9/prebuilt/linux-x86_64/ --strip-components 1 \
	&& rm -f $(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM64) \
	&& rm -rf $(ANDROID_NDK_HOME_LEGACY)/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/ \
	&& mkdir  $(ANDROID_NDK_HOME_LEGACY)/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/ \
	&& tar -xf $(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM) -C $(ANDROID_NDK_HOME_LEGACY)/toolchains/arm-linux-androideabi-4.9/prebuilt/linux-x86_64/ --strip-components 1 \
	&& rm -f $(ANDROID_NDK_GFORTRAN_ARCHIVE_ARM)



# updates Android SDK, install Android API, Build Tools and accept licenses
update_android_sdk:
	touch $(ANDROID_HOME)/repositories.cfg
	yes | $(ANDROID_SDK_HOME)/tools/bin/sdkmanager --sdk_root=$(ANDROID_SDK_HOME) --licenses > /dev/null
	$(ANDROID_SDK_HOME)/tools/bin/sdkmanager --sdk_root=$(ANDROID_SDK_HOME) "build-tools;$(ANDROID_SDK_BUILD_TOOLS_VERSION)" > /dev/null
	$(ANDROID_SDK_HOME)/tools/bin/sdkmanager --sdk_root=$(ANDROID_SDK_HOME) "platforms;android-$(ANDROID_API_LEVEL)" > /dev/null
	# Set avdmanager permissions (executable)
	chmod +x $(ANDROID_SDK_HOME)/tools/bin/avdmanager
