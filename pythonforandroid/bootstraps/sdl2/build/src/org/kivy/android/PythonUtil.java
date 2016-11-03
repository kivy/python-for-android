package org.kivy.android;

import java.io.File;

import android.util.Log;
import java.util.ArrayList;
import java.io.FilenameFilter;

public class PythonUtil {
	private static final String TAG = "pythonutil";

    protected static ArrayList<String> getLibraries(File filesDir) {

        ArrayList<String> MyList = new ArrayList<String>();
        MyList.add("SDL2");
        MyList.add("SDL2_image");
        MyList.add("SDL2_mixer");
        MyList.add("SDL2_ttf");

        String absPath = filesDir.getParentFile().getParentFile().getAbsolutePath() + "/lib/";
        filesDir = new File(absPath);
        File [] files = filesDir.listFiles(new FilenameFilter() {
            @Override
            public boolean accept(File dir, String name) {
                return  name.matches(".*ssl.*") || name.matches(".*crypto.*");
            }
        });

        for (int i = 0; i < files.length; ++i) {
            File mfl = files[i];
            String name = mfl.getName();
            name = name.substring(3, name.length() - 3);
            MyList.add(name);
        };

        MyList.add("python2.7");
        MyList.add("python3.5m");
        MyList.add("main");
        return MyList;
    }

    public static void loadLibraries(File filesDir) {

        String filesDirPath = filesDir.getAbsolutePath();
        boolean foundPython = false;

		for (String lib : getLibraries(filesDir)) {
            Log.v(TAG, "Loading library: " + lib);
		    try {
                System.loadLibrary(lib);
                if (lib.startsWith("python")) {
                    foundPython = true;
                }
            } catch(UnsatisfiedLinkError e) {
                // If this is the last possible libpython
                // load, and it has failed, give a more
                // general error
                Log.v(TAG, "Library loading error: " + e.getMessage());
                if (lib.startsWith("python3.6") && !foundPython) {
                    throw new java.lang.RuntimeException("Could not load any libpythonXXX.so");
                } else if (lib.startsWith("python")) {
                    continue;
                } else {
                    Log.v(TAG, "An UnsatisfiedLinkError occurred loading " + lib);
                    throw e;
                }
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

