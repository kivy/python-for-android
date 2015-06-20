from distutils.core import setup, Extension
import os

setup(name='android',
      version='1.0',
      packages=['android'],
      package_dir={'android': 'android'},
      ext_modules=[

        Extension(
            'android._android', ['android/_android.c', 'android/_android_jni.c'],
            libraries=[ 'sdl', 'log' ],
            library_dirs=[ 'libs/' + os.environ['ARCH'] ],
            ),
        Extension(
            'android._android_billing', ['android/_android_billing.c', 'android/_android_billing_jni.c'],
            libraries=[ 'log' ],
            library_dirs=[ 'libs/' + os.environ['ARCH'] ],
            ),
        Extension(
            'android._android_sound', ['android/_android_sound.c', 'android/_android_sound_jni.c',],
            libraries=[ 'sdl', 'log' ],
            library_dirs=[ 'libs/' + os.environ['ARCH'] ],
            ),

        ]
      )
