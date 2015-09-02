from pythonforandroid.toolchain import Recipe, shprint, current_directory
import os
import platform
import sh

class Qt5Recipe(Recipe):
    version = "5.5.0"
    url     = 'http://download.qt.io/official_releases/qt/%s/%s/single/qt-everywhere-opensource-src-%s.tar.gz' %(version[:version.rfind(".")], version, version)
    #md5sum = '828594c91ba736ce2cd3e1e8a6146452' ## TODO: Causes an error
    name    = 'qt5'

    #depends = ['libxml2', 'libxslt'] ## Couldn't find it currently here

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = os.environ.copy()

            env['ANDROID_API_VERSION'] = "android-%s" %(self.ctx.android_api) # Absolutly needed during build process of 5.5.0

            configure = sh.Command('./configure')
            shprint(configure,
                    '-xplatform',                 'android-g++',
                    '-prefix',                    os.path.join(self.get_build_dir(arch.arch), "qt5-install"),
                    '-hostprefix',                os.path.join(self.get_build_dir('host'),    "qt5-install"),
                    '-nomake',                    'tests',
                    '-nomake',                    'examples',
                    '-android-arch',              arch.arch,
                    '-android-sdk',               self.ctx.sdk_dir,
                    '-android-ndk',               self.ctx.ndk_dir,
                    '-android-ndk-platform',      'android-%s' %(self.ctx.android_api),
                    '-android-ndk-host',          "linux-%s" %(platform.processor()),
                    '-android-toolchain-version', self.ctx.toolchain_version,
                    '-skip',                      'qt3d',              # Causes an install problem
                    #'-skip',                      'qtactiveqt5',
                    #'-skip',                      'qtandroidextras',
                    #'-skip',                      'qtbase',
                    '-skip',                      'qtcanvas3d',        # Causes an install problem
                    #'-skip',                      'qtconnectivity',
                    #'-skip',                      'qtdeclarative',
                    '-skip',                      'qtdoc',
                    #'-skip',                      'qtenginio',
                    #'-skip',                      'qtgraphicaleffects',
                    #'-skip',                      'qtimageformats',
                    #'-skip',                      'qtlocation',
                    #'-skip',                      'qtmacextras',
                    #'-skip',                      'qtmultimedia',
                    #'-skip',                      'qtquick1',
                    #'-skip',                      'qtquickcontrols',
                    #'-skip',                      'qtscript',
                    #'-skip',                      'qtsensors',
                    #'-skip',                      'qtserialport',
                    #'-skip',                      'qtsvg',
                    '-skip',                      'qttools',
                    #'-skip',                      'qttranslations',
                    #'-skip',                      'qtwayland',
                    #'-skip',                      'qtwebchannel',
                    #'-skip',                      'qtwebengine',
                    #'-skip',                      'qtwebkit',
                    '-skip',                      'qtwebkit-examples',
                    #'-skip',                      'qtwebsockets',
                    #'-skip',                      'qtwinextras',
                    #'-skip',                      'qtx11extras',
                    #'-skip',                      'qtxmlpatterns',
                    '-qt-pcre',
                    '-no-warnings-are-errors',
                    '-opensource', '-confirm-license',
                    '-silent',
                    _env=env)

            make = sh.Command("make")
            shprint(make, '-j5', _env=env)
            shprint(make, '-j5', 'install', _env=env)


recipe = Qt5Recipe()
