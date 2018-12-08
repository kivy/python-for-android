package org.kivy.android;

import java.io.File;

import android.util.Log;
import android.app.Activity;
import android.content.res.AssetManager;

import java.util.ArrayList;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.FileNotFoundException;
import java.io.IOException;

public class PythonUtil {
	private static final String TAG = "PythonUtil";

    protected static ArrayList<String> getLibraries(Activity activity) {
        AssetManager assets = activity.getAssets();

        StringBuilder sb = new StringBuilder();
        ArrayList<String> libsList = new ArrayList<String>();
        BufferedReader reader = null;
        try {
            reader = new BufferedReader(
                new InputStreamReader(assets.open("libraries_to_load.txt")));
            String mLine;
            while ((mLine = reader.readLine()) != null) {
                libsList.add(mLine);
             }
        } catch (IOException e) {
            Log.v(TAG, "Error reading Libraries file...no libs will be added");
        } finally {
            if (reader != null) {
                 try {
                     reader.close();
                 } catch (IOException e) {
                    Log.v(TAG, "Error on closing libraries file...going on");
                 }
            }
        }
        libsList.add("main");
        return libsList;
    }

    public static void loadLibraries(Activity activity) {

        boolean foundPython = false;

		for (String lib : getLibraries(activity)) {
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
                if (lib.startsWith("python3.7") && !foundPython) {
                    throw new java.lang.RuntimeException("Could not load any libpythonXXX.so");
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
