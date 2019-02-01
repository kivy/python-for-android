from pythonforandroid.toolchain import Recipe, current_directory, shprint
from os.path import exists, join, realpath
import sh


class FFMpegRecipe(Recipe):
    version = '3.4.5'
    url = 'http://ffmpeg.org/releases/ffmpeg-{version}.tar.bz2'
    depends = ['sdl2']  # Need this to build correct recipe order
    opts_depends = ['openssl', 'ffpyplayer_codecs']
    patches = ['patches/configure.patch']

    def should_build(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        return not exists(join(build_dir, 'lib', 'libavcodec.so'))

    def prebuild_arch(self, arch):
        self.apply_patches(arch)

    def get_recipe_env(self, arch):
        env = super(FFMpegRecipe, self).get_recipe_env(arch)
        env['NDK'] = self.ctx.ndk_dir
        return env

    def build_arch(self, arch):
        with current_directory(self.get_build_dir(arch.arch)):
            env = arch.get_env()

            flags = ['--disable-everything']
            cflags = []
            ldflags = []

            if 'openssl' in self.ctx.recipe_build_order:
                flags += [
                    '--enable-openssl',
                    '--enable-nonfree',
                    '--enable-protocol=https,tls_openssl',
                ]
                build_dir = Recipe.get_recipe('openssl', self.ctx).get_build_dir(arch.arch)
                cflags += ['-I' + build_dir + '/include/']
                ldflags += ['-L' + build_dir]

            if 'ffpyplayer_codecs' in self.ctx.recipe_build_order:
                # libx264
                flags += ['--enable-libx264']
                build_dir = Recipe.get_recipe('libx264', self.ctx).get_build_dir(arch.arch)
                cflags += ['-I' + build_dir + '/include/']
                ldflags += ['-lx264', '-L' + build_dir + '/lib/']

                # libshine
                flags += ['--enable-libshine']
                build_dir = Recipe.get_recipe('libshine', self.ctx).get_build_dir(arch.arch)
                cflags += ['-I' + build_dir + '/include/']
                ldflags += ['-lshine', '-L' + build_dir + '/lib/']

                # Enable all codecs:
                flags += [
                    '--enable-parsers',
                    '--enable-decoders',
                    '--enable-encoders',
                    '--enable-muxers',
                    '--enable-demuxers',
                ]
            else:
                # Enable codecs only for .mp4:
                flags += [
                    '--enable-parser=aac,ac3,h261,h264,mpegaudio,mpeg4video,mpegvideo,vc1',
                    '--enable-decoder=aac,h264,mpeg4,mpegvideo',
                    '--enable-muxer=h264,mov,mp4,mpeg2video',
                    '--enable-demuxer=aac,h264,m4v,mov,mpegvideo,vc1',
                ]

            # needed to prevent _ffmpeg.so: version node not found for symbol av_init_packet@LIBAVFORMAT_52
            # /usr/bin/ld: failed to set dynamic section sizes: Bad value
            flags += [
                '--disable-symver',
            ]

            # disable binaries / doc
            flags += [
                '--disable-ffmpeg',
                '--disable-ffplay',
                '--disable-ffprobe',
                '--disable-ffserver',
                '--disable-doc',
            ]

            # other flags:
            flags += [
                '--enable-filter=aresample,resample,crop,adelay,volume,scale',
                '--enable-protocol=file,http',
                '--enable-small',
                '--enable-hwaccels',
                '--enable-gpl',
                '--enable-pic',
                '--disable-static',
                '--enable-shared',
            ]

            # android:
            flags += [
                '--target-os=android',
                '--cross-prefix=arm-linux-androideabi-',
                '--arch=arm',
                '--sysroot=' + self.ctx.ndk_platform,
                '--enable-neon',
                '--prefix={}'.format(realpath('.')),
            ]
            cflags += [
                '-mfpu=vfpv3-d16',
                '-mfloat-abi=softfp',
                '-fPIC',
            ]

            env['CFLAGS'] += ' ' + ' '.join(cflags)
            env['LDFLAGS'] += ' ' + ' '.join(ldflags)

            configure = sh.Command('./configure')
            shprint(configure, *flags, _env=env)
            shprint(sh.make, '-j4', _env=env)
            shprint(sh.make, 'install', _env=env)
            # copy libs:
            sh.cp('-a', sh.glob('./lib/lib*.so'), self.ctx.get_libs_dir(arch.arch))


recipe = FFMpegRecipe()
