package org.kivy.android;

import java.io.File;

import android.util.Log;


public class PythonUtil {
	private static final String TAG = "PythonUtil";

	protected static String[] getLibraries() {
        return new String[] {
            "SDL2",
            "SDL2_image",
            "SDL2_mixer",
            "SDL2_ttf",
            "python2.7",
            "main"
        };
    }

	public static void loadLibraries(File filesDir) {
		for (String lib : getLibraries()) {
			System.loadLibrary(lib);
		}

		System.load(filesDir + "/lib/python2.7/lib-dynload/_io.so");
		System.load(filesDir + "/lib/python2.7/lib-dynload/unicodedata.so");

		try {
			System.load(filesDir + "/lib/python2.7/lib-dynload/_ctypes.so");
		} catch(UnsatisfiedLinkError e) {
			Log.v(TAG, "Unsatisfied linker when loading ctypes");
		}

		Log.v(TAG, "Loaded everything!");
	}
}
