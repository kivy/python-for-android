Contribute
==========

Extending Python for android native support
-------------------------------------------

So, you want to get into python-for-android and extend what's available
to Python on Android ?

Turns out it's not very complicated, here is a little introduction on how to go
about it. Without Pyjnius, the schema to access the Java API from Cython is::

    [1] Cython -> [2] C JNI -> [3] Java

Think about acceleration sensors: you want to get the acceleration
values in Python, but nothing is available natively. Lukcily you have
a Java API for that : the Google API is available here
http://developer.android.com/reference/android/hardware/Sensor.html

You can't use it directly, you need to do your own API to use it in python,
this is done in 3 steps

Step 1: write the java code to create very simple functions to use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

like : accelerometer Enable/Reading
In our project, this is done in the Hardware.java:
https://github.com/kivy/python-for-android/blob/master/src/src/org/renpy/android/Hardware.java
you can see how it's implemented

Step 2 : write a jni wrapper
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a C file to be able to invoke/call Java functions from C, in our case,
step 2 (and 3) are done in the android python module. The JNI part is done in
the android_jni.c:
https://github.com/kivy/python-for-android/blob/master/recipes/android/src/android_jni.c

Step 3 : you have the java part, that you can call from the C
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can now do the Python extension around it, all the android python part is
done in
https://github.com/kivy/python-for-android/blob/master/recipes/android/src/android.pyx

→ [python] android.accelerometer_reading ⇒ [C] android_accelerometer_reading
⇒ [Java] Hardware.accelerometer_reading()

The jni part is really a C api to call java methods. a little bit hard to get
it with the syntax, but working with current example should be ok

Example with bluetooth
~~~~~~~~~~~~~~~~~~~~~~
Start directly from a fork of https://github.com/kivy/python-for-android

The first step is to identify where and how they are doing it in sl4a, it's
really easy, because everything is already done as a client/server
client/consumer approach, for bluetooth, they have a "Bluetooth facade" in
java.

http://code.google.com/p/android-scripting/source/browse/android/BluetoothFacade/src/com/googlecode/android_scripting/facade/BluetoothFacade.java

You can learn from it, and see how is it's can be used as is, or if you can
simplify / remove stuff you don't want.

From this point, create a bluetooth file in
python-for-android/tree/master/src/src/org/renpy/android in Java.

Do a good API (enough simple to be able to write the jni in a very easy manner,
like, don't pass any custom java object in argument).

Then write the JNI, and then the python part.

3 steps, once you get it, the real difficult part is to write the java part :)

Jni gottchas
~~~~~~~~~~~~

- package must be org.renpy.android, don't change it.


Create your own recipes
-----------------------

A recipe is a script that contains the "definition" of a module to compile.
The directory layout of a recipe for a <modulename> is something like::

    python-for-android/recipes/<modulename>/recipe.sh
    python-for-android/recipes/<modulename>/patches/
    python-for-android/recipes/<modulename>/patches/fix-path.patch

When building, all the recipe builds must go to::

    python-for-android/build/<modulename>/<archiveroot>

For example, if you want to create a recipe for sdl, do::

    cd python-for-android/recipes
    mkdir sdl
    cp recipe.sh.tmpl sdl/recipe.sh
    sed -i 's#XXX#sdl#' sdl/recipe.sh

Then, edit the sdl/recipe.sh to adjust other information (version, url) and
complete the build function.

