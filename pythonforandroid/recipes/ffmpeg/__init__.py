from pythonforandroid.toolchain import Recipe, shprint, current_directory, ArchARM
from os.path import exists, join, realpath
from os import uname
import glob
import sh
import os
import shutil


class FFMpegRecipe(Recipe):
    version = '2.8.8'
    url = 'http://ffmpeg.org/releases/ffmpeg-{version}.tar.bz2'
    depends = ['openssl', 'ffpyplayer_codecs']  # TODO should be opts_depends
    patches = ['patches/fix-libshine-configure.patch']

    # TODO add should_build(self, arch)

    def prebuild_arch(self, arch):
        self.apply_patches(arch)

    def get_recipe_env(self,arch):
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
                    '--enable-parser=h264,aac',
                    '--enable-decoder=h263,h264,aac',
                ]

                # disable some unused algo
                # note: "golomb" are the one used in our video test, so don't use --disable-golomb
                # note: and for aac decoding: "rdft", "mdct", and "fft" are needed
                flags += [
                    '--disable-dxva2 --disable-vdpau --disable-vaapi',
                    '--disable-dct',
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
                '--enable-filter=aresample,resample,crop,adelay,volume',
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
            cflags = [
                '-march=armv7-a', 
                '-mfpu=vfpv3-d16', 
                '-mfloat-abi=softfp', 
                '-fPIC', 
                '-DANDROID',
            ] + cflags

            env['CFLAGS'] += ' ' + ' '.join(cflags)
            env['LDFLAGS'] += ' ' + ' '.join(ldflags)

            configure = sh.Command('./configure')
            shprint(configure, *flags, _env=env)
            shprint(sh.make, '-j4', _env=env)
            shprint(sh.make, 'install', _env=env)
            # copy libs:
            sh.cp('-a', sh.glob('./lib/lib*.so'), self.ctx.get_libs_dir(arch.arch))

recipe = FFMpegRecipe()
