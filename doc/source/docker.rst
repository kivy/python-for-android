.. _docker:

Docker
======

Currently we use a containerized build for testing Python for Android recipes.
Docker supports three big platforms either directly with the kernel or via
using headless VirtualBox and a small distro to run itself on.

While this is not the actively supported way to build applications, if you are
willing to play with the approach, you can use the ``Dockerfile`` to build
the Docker image we use for CI builds and create an Android
application with that in a container. This approach allows you to build Android
applications on all platforms Docker engine supports. These steps assume you
already have Docker preinstalled and set up.

.. warning::
   This approach is highly space unfriendly! The more layers (``commit``) or
   even Docker images (``build``) you create the more space it'll consume.
   Within the Docker image there is Android SDK and NDK + various dependencies.
   Within the custom diff made by building the distribution there is another
   big chunk of space eaten. The very basic stuff such as a distribution with:
   CPython 3, setuptools, Python for Android ``android`` module, SDL2 (+ deps),
   PyJNIus and Kivy takes almost 2 GB. Check your free space first!

1. Clone the repository::

       git clone https://github.com/kivy/python-for-android

2. Build the image with name ``p4a``::

       docker build --tag p4a .

   .. note::
      You need to be in the ``python-for-android`` for the Docker build context
      and you can optionally use ``--file`` flag to specify the path to the
      ``Dockerfile`` location.

3. Create a container from ``p4a`` image with copied ``testapps`` folder
   in the image mounted to the same one in the cloned repo on the host::

       docker run \
           --interactive \
           --tty \
           --volume ".../testapps":/home/user/testapps \
           p4a sh -c
               '. venv/bin/activate \
               && cd testapps \
               && python setup_testapp_python3.py apk \
               --sdk-dir $ANDROID_SDK_HOME \
               --ndk-dir $ANDROID_NDK_HOME'

   .. note::
      On Windows you might need to use quotes and forward-slash path for volume
      "/c/Users/.../python-for-android/testapps":/home/user/testapps

   .. warning::
      On Windows ``gradlew`` will attempt to use 'bash\r' command which is
      a result of Windows line endings. For that you'll need to install
      ``dos2unix`` package into the image.

4. Preserve the distribution you've already built (optional, but recommended):

       docker commit $(docker ps --last=1 --quiet) my_p4a_dist

5. Find the ``.APK`` file on this location::

       ls -lah testapps
