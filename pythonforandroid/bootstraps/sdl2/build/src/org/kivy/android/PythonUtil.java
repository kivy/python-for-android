package org.kivy.android;

import java.io.File;

import android.util.Log;


public class PythonUtil {
    private static final String TAG = "PythonUtil";

    protected static ArrayList<String> getLibraries(File filesDir) {

        // XXX: read libraries/patterns to be loaded from default path from
        //      file or generated class or similar

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
                return name.matches(".*ssl.*")
                    || name.matches(".*crypto.*")
                    || name.matches(".*ffi.*");
            }
        });

	private static final String TAG = "PythonUtil";

	protected static String[] getLibraries() {
        return new String[] {
            "SDL2",
            "SDL2_image",
            "SDL2_mixer",
            "SDL2_ttf",
            "crypto1.0.2h",
            "ssl1.0.2h",
            "python2.7",
            "python3.5m",
            "main"
        };

        MyList.add("python2.7");
        MyList.add("python3.5m");
        MyList.add("main");
        return MyList;
    }

	public static void loadLibraries(File filesDir) {

        String filesDirPath = filesDir.getAbsolutePath();
        boolean skippedPython = false;

		for (String lib : getLibraries()) {
		    try {
                System.loadLibrary(lib);
            } catch(UnsatisfiedLinkError e) {
                if (lib.startsWith("python") && !skippedPython) {
                    skippedPython = true;
                    continue;
                }
                throw e;
            }
        }

        // XXX: read libraries to be loaded from custom path from
        //      file or generated class or similar

        try {
            System.load(filesDirPath + "/lib/python2.7/lib-dynload/_io.so");
            System.load(filesDirPath + "/lib/python2.7/lib-dynload/unicodedata.so");
        } catch(UnsatisfiedLinkError e) {
            Log.v(TAG, "Failed to load _io.so or unicodedata.so...but that's okay.");
        }
        
        try {
            System.load(filesDirPath + "/lib/python2.7/lib-dynload/_ctypes.so");
        } catch(UnsatisfiedLinkError e) {
            Log.v(TAG, "Unsatisfied linker when loading ctypes");
        }

        // try {
        //     System.load(filesDirPath + "/lib/python2.7/site-packages/_cffi_backend.so");
        // } catch(UnsatisfiedLinkError e) {
        //     Log.v(TAG, "Unsatisfied linker when loading cffi backend");
        // }

        Log.v(TAG, "Loaded everything!");
	}
}
