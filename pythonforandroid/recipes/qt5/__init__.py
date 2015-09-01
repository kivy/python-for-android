from pythonforandroid.toolchain import Recipe, shprint, get_directory, current_directory, ArchAndroid, info
from os.path import exists, join, realpath
from os import uname, environ
import glob
import sh

class Qt5Recipe(Recipe):
    version = "5.5.0"
    url     = 'http://download.qt.io/official_releases/qt/%s/%s/single/qt-everywhere-opensource-src-%s.tar.gz' %(version[:3], version, version)
    #md5sum = '828594c91ba736ce2cd3e1e8a6146452'
    name    = 'qt5'

    #depends = ['libxml2', 'libxslt']  

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = environ.copy()

            env['ANDROID_API_VERSION'] = "android-%s" %(env['ANDROIDAPI'])
            env['ANDROID_SDK_ROOT']    = env['ANDROIDSDK']
            env['ANDROID_NDK_ROOT']    = env['ANDROIDNDK']
            env['ANDROID_ARCH']        = arch.arch
            env['ANDROID_HOST']        = "linux-x86_64"
            env['ANDROID_TOOLCHAIN']   = "4.9"
                        
            configure = sh.Command('./configure')
            shprint(configure,
                    '-xplatform',                 'android-g++',
                    '-prefix',                    '%s-install' %(self.get_build_dir(arch.arch)),
                    '-hostprefix',                '%s-install' %(self.get_build_dir('host')),
                    '-nomake',                    'tests',
                    '-nomake',                    'examples',
                    '-android-arch',              env['ANDROID_ARCH'],
                    '-android-sdk',               env['ANDROID_SDK_ROOT'],
                    '-android-ndk',               env['ANDROID_NDK_ROOT'],
                    '-android-ndk-platform',      'android-%s' %(env['ANDROIDAPI']),
                    '-android-ndk-host',          env['ANDROID_HOST'],
                    '-android-toolchain-version', env['ANDROID_TOOLCHAIN'],
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
                    '-skip',                      'qtwebkit',
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
            

        # print('python2 build done, exiting for debug')
        # exit(1)


recipe = Qt5Recipe()
