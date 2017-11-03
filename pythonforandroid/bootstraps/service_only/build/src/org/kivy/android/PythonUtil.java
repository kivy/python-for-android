package org.kivy.android;

import android.util.Log;

import java.io.File;

public class PythonUtil {
    private static String TAG = PythonUtil.class.getSimpleName();

    protected static String[] getLibraries() {
        return new String[]{
                "python2.7",
                "main",
                "/lib/python2.7/lib-dynload/_io.so",
                "/lib/python2.7/lib-dynload/unicodedata.so",
                "/lib/python2.7/lib-dynload/_ctypes.so",
        };
    }

    public static void loadLibraries(File filesDir) {
        String filesDirPath = filesDir.getAbsolutePath();
        Log.v(TAG, "Loading libraries from " + filesDirPath);

        for (String lib : getLibraries()) {
            if (lib.startsWith("/")) {
                System.load(filesDirPath + lib);
            } else {
                System.loadLibrary(lib);
            }
        }

        Log.v(TAG, "Loaded everything!");
    }
}
