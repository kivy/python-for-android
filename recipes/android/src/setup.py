from distutils.core import setup, Extension
import os

setup(name='android',
      version='1.0',
      ext_modules=[

        Extension(
            'android', ['android.c', 'android_jni.c'],
            libraries=[ 'sdl', 'log' ],
            library_dirs=[ 'libs/'+os.environ['ARCH'] ],
            ),
        Extension(
            'android_billing', ['android_billing.c', 'android_billing_jni.c'],
            libraries=[ 'log' ],
            library_dirs=[ 'libs/'+os.environ['ARCH'] ],
            ),
        Extension(
            'android_sound', ['android_sound.c', 'android_sound_jni.c',],
            libraries=[ 'sdl', 'log' ],
            library_dirs=[ 'libs/'+os.environ['ARCH'] ],
            ),

        ]
      )
