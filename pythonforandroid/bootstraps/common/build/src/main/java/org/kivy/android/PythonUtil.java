package org.kivy.android;

import java.io.File;

import android.util.Log;
import java.util.ArrayList;
import java.util.regex.Pattern;


public class PythonUtil {
	private static final String TAG = "pythonutil";

    protected static void addLibraryIfExists(ArrayList<String> libsList, String pattern, File libsDir) {
        // pattern should be the name of the lib file, without the
        // preceding "lib" or suffix ".so", for instance "ssl.*" will
        // match files of the form "libssl.*.so".
        File [] files = libsDir.listFiles();

        pattern = "lib" + pattern + "\\.so";
        Pattern p = Pattern.compile(pattern);
        for (int i = 0; i < files.length; ++i) {
            File file = files[i];
            String name = file.getName();
            Log.v(TAG, "Checking pattern " + pattern + " against " + name);
            if (p.matcher(name).matches()) {
                Log.v(TAG, "Pattern " + pattern + " matched file " + name);
                libsList.add(name.substring(3, name.length() - 3));
            }
        }
    }

    protected static ArrayList<String> getLibraries(File libsDir) {
        ArrayList<String> libsList = new ArrayList<String>();
        addLibraryIfExists(libsList, "sqlite3", libsDir);
        addLibraryIfExists(libsList, "ffi", libsDir);
        addLibraryIfExists(libsList, "png16", libsDir);
        addLibraryIfExists(libsList, "ssl.*", libsDir);
        addLibraryIfExists(libsList, "crypto.*", libsDir);
        addLibraryIfExists(libsList, "SDL2", libsDir);
        addLibraryIfExists(libsList, "SDL2_image", libsDir);
        addLibraryIfExists(libsList, "SDL2_mixer", libsDir);
        addLibraryIfExists(libsList, "SDL2_ttf", libsDir);
        libsList.add("python3.5m");
        libsList.add("python3.6m");
        libsList.add("python3.7m");
        libsList.add("python3.8m");
        libsList.add("main");
        return libsList;
    }

    public static void loadLibraries(File filesDir, File libsDir) {
        boolean foundPython = false;

        for (String lib : getLibraries(libsDir)) {
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
                if (lib.startsWith("python3.8") && !foundPython) {
                    throw new RuntimeException("Could not load any libpythonXXX.so");
                } else if (lib.startsWith("python")) {
                    continue;
                } else {
                    Log.v(TAG, "An UnsatisfiedLinkError occurred loading " + lib);
                    throw e;
                }
            }
        }

        Log.v(TAG, "Loaded everything!");
    }
}
