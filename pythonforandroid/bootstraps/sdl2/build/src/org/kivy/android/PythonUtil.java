package org.kivy.android;

import java.io.File;

import android.util.Log;
import java.util.ArrayList;
import java.io.FilenameFilter;

public class PythonUtil {
    private static final String TAG = "PythonUtil";

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
                return name.matches(".*ssl.*")
                    || name.matches(".*crypto.*")
                    || name.matches(".*ffi.*");
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
        boolean skippedPython = false;

        for (String lib : getLibraries(filesDir)) {
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

        try {
            System.load(filesDirPath + "/lib/python2.7/site-packages/_cffi_backend.so");
        } catch(UnsatisfiedLinkError e) {
            Log.v(TAG, "Unsatisfied linker when loading cffi backend");
        }

        Log.v(TAG, "Loaded everything!");
    }
}

