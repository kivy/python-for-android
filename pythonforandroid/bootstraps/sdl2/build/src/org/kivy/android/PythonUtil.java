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
            "python3.5m",
            "main"
        };
    }

	public static void loadLibraries(File filesDir) {

        String filesDirPath = filesDir.getAbsolutePath();
        boolean skippedPython = false;

		for (String lib : getLibraries()) {
		    try {
                System.loadLibrary(lib);
            } catch(UnsatisfiedLinkError e) {
                if (lib.startsWith("python")){
                    Log.v(TAG, e.getMessage());
                    Log.v(TAG, "It's ok not to load python2 library for python3 app and vice versa.");
                    if (!skippedPython) {
                        skippedPython = true;
                        continue;
                    }
                }
                throw e;
            }
        }

        try {
            System.load(filesDirPath + "/lib/python2.7/lib-dynload/_io.so");
            System.load(filesDirPath + "/lib/python2.7/lib-dynload/unicodedata.so");
        } catch(UnsatisfiedLinkError e) {
            Log.v(TAG, "Failed to load _io.so or unicodedata.so...but that's okay.");
        }
        
        try {
            // System.loadLibrary("ctypes");
            System.load(filesDirPath + "/lib/python2.7/lib-dynload/_ctypes.so");
        } catch(UnsatisfiedLinkError e) {
            Log.v(TAG, "Unsatisfied linker when loading ctypes");
        }

        Log.v(TAG, "Loaded everything!");
	}
}
