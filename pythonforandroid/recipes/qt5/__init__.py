from pythonforandroid.toolchain import Recipe, shprint, current_directory, info, warning
import os
import platform
import multiprocessing
import sh

class Qt5Recipe(Recipe):
    version = "5.5.0"
    url     = 'http://download.qt.io/official_releases/qt/%s/%s/single/qt-everywhere-opensource-src-%s.tar.gz' %(version[:version.rfind(".")], version, version)
    #url      = 'git://github.com/qtproject/qt5.git'
    #md5sum = '828594c91ba736ce2cd3e1e8a6146452' ## TODO: Causes an error
    name    = 'qt5'

    #depends = ['libxml2', 'libxslt'] ## Couldn't find it currently here

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = os.environ.copy()

            env['ANDROID_API_VERSION'] = "android-%s" %(self.ctx.android_api) # Absolutly needed during build process of 5.5.0

            skip_bug_install = ('-skip',                      'qt3d',              # Causes an install problem
                                '-skip',                      'qtcanvas3d',        # Causes an install problem
                                )
            skip_for_lightweight = ('-skip',                      'qtdoc',
                                    '-skip',                      'qttools',
                                    '-skip',                      'qtwebkit-examples'
                                   )

            # According to http://wiki.qt.io/Android there are qt5 components, which depend on a specific Android API
            skip_incompatible_api = ()
            notified_about_api    = False
            if self.ctx.android_api < 11:
                if not notified_about_api:
                    info("Android API is lower than 11!")
                    notified_about_api = True
                warning("* therefore QtMultimedia will be disabled...")
                skip_incompatible_api += ('-skip', 'qtmultimedia')
            if self.ctx.android_api < 16:
                if not notified_about_api:
                    info("Android API is lower than 16!")
                    notified_about_api = True
                warning("* therefore QtBase will be disabled...")
                skip_incompatible_api += ('-skip', 'qtbase')
            if self.ctx.android_api < 18:
                if not notified_about_api:
                    info("Android API is lower than 18!")
                    notified_about_api = True
                warning("* therefore QtConnectivity will be disabled...")
                skip_incompatible_api += ('-skip', 'qtconnectivity')

            configure_command = sh.Command('./configure')
            configure_arguments = ('-xplatform',                 'android-g++',
                                   '-prefix',                    os.path.join(self.get_build_dir(arch.arch), "qt5-install"),
                                   '-hostprefix',                os.path.join(self.get_build_dir('host'),    "qt5-install"),
                                   '-nomake',                    'tests',
                                   '-nomake',                    'examples',
                                   '-android-arch',              arch.arch,
                                   '-android-sdk',               self.ctx.sdk_dir,
                                   '-android-ndk',               self.ctx.ndk_dir,
                                   '-android-ndk-platform',      'android-%s' %(self.ctx.android_api),
                                   '-android-ndk-host',          "linux-%s" %(platform.machine()),
                                   '-android-toolchain-version', self.ctx.toolchain_version,
                                   ## In case you don't need one of the components, just uncommend one of them above:
                                   #'-skip',                      'qt3d',
                                   #'-skip',                      'qtactiveqt5',
                                   #'-skip',                      'qtandroidextras',
                                   #'-skip',                      'qtbase',
                                   #'-skip',                      'qtcanvas3d',
                                   #'-skip',                      'qtconnectivity',
                                   #'-skip',                      'qtdeclarative',
                                   #'-skip',                      'qtdoc',
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
                                   #'-skip',                      'qttools',
                                   #'-skip',                      'qttranslations',
                                   #'-skip',                      'qtwayland',
                                   #'-skip',                      'qtwebchannel',
                                   #'-skip',                      'qtwebengine',
                                   #'-skip',                      'qtwebkit',
                                   #'-skip',                      'qtwebkit-examples',
                                   #'-skip',                      'qtwebsockets',
                                   #'-skip',                      'qtwinextras',
                                   #'-skip',                      'qtx11extras',
                                   #'-skip',                      'qtxmlpatterns',
                                   '-no-warnings-are-errors',
                                   '-opensource', '-confirm-license',
                                   '-silent')

            #if "zlib" in self.ctx.recipes:
            configure_arguments = configure_arguments + ('-qt-zlib',)
            #else:
            #    configure_arguments = configure_arguments + ('-system-zlib',)

            #if "libjpeg" in self.ctx.recipes:
            configure_arguments = configure_arguments + ('-qt-libjpeg',)
            #else:
            #    configure_arguments = configure_arguments + ('-system-libjpeg',)

            #if "libpng" in self.ctx.recipes:
            configure_arguments = configure_arguments + ('-qt-libpng',)
            #else:
            #    configure_arguments = configure_arguments + ('-system-libpng',)

            #if "xcb" in self.ctx.recipes:
            #configure_arguments = configure_arguments + ('-qt-xcb',) # Causes an test error when configuring
            #else:
            #    configure_arguments = configure_arguments + ('-system-xcb',)

            #if "xkbcommon" in self.ctx.recipes:
            configure_arguments = configure_arguments + ('-qt-xkbcommon',)
            #else:
            #    configure_arguments = configure_arguments + ('-system-xkbcommon',)

            #if "freetype" in self.ctx.recipes:
            configure_arguments = configure_arguments + ('-qt-freetype',)
            #else:
            #    configure_arguments = configure_arguments + ('-system-freetype',)

            #if "PCRE" in self.ctx.recipes:
            configure_arguments = configure_arguments + ('-qt-pcre',)
            #else:
            #    configure_arguments = configure_arguments + ('-system-pcre',)

            #if "harfbuzz" in self.ctx.recipes:
            configure_arguments = configure_arguments + ('-qt-harfbuzz',)
            #else:
            #    configure_arguments = configure_arguments + ('-system-harfbuzz',)

            if skip_incompatible_api:
                configure_arguments = configure_arguments + skip_incompatible_api

            configure_arguments = configure_arguments + skip_bug_install + skip_for_lightweight

            shprint(configure_command,
                    *configure_arguments,
                    _env=env)

            make      = sh.Command("make")
            make_jobs = "-j{}".format(multiprocessing.cpu_count()+1)
            shprint(make, make_jobs, _env=env)
            shprint(make, make_jobs, 'install', _env=env)

    def postbuild_arch(self, arch):
        with current_directory(os.path.join(self.get_build_dir(arch.arch), "qt5-install")):
            info('Copying Qt5 java classes...')
            shprint(sh.cp, '-a', join('jar', '*.jar'), self.ctx.javaclass_dir)
            info('Copying Qt5 libraries...')
            shprint(sh.cp, '-a', join('lib', '*.so'), self.ctx.get_libs_dir(arch.arch))
            #info('Copying Qt5 QML...')
            #shprint(sh.cp, '-a', join('qml'), self.ctx.qml_dir)

recipe = Qt5Recipe()
