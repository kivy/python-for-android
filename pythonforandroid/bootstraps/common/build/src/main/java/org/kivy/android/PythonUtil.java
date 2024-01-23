package org.kivy.android;

import java.io.InputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.File;

import android.app.Activity;
import android.content.Context;
import android.content.res.Resources;
import android.util.Log;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.regex.Pattern;

import org.renpy.android.AssetExtract;

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
        libsList.add("python3.8");
        libsList.add("python3.9");
        libsList.add("python3.10");
        libsList.add("python3.11");
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
                if (lib.startsWith("python3.11") && !foundPython) {
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

    public static String getAppRoot(Context ctx) {
        String appRoot = ctx.getFilesDir().getAbsolutePath() + "/app";
        return appRoot;
    }

    public static String getResourceString(Context ctx, String name) {
        // Taken from org.renpy.android.ResourceManager
        Resources res = ctx.getResources();
        int id = res.getIdentifier(name, "string", ctx.getPackageName());
        return res.getString(id);
    }

    /**
     * Show an error using a toast. (Only makes sense from non-UI threads.)
     */
    protected static void toastError(final Activity activity, final String msg) {
        activity.runOnUiThread(new Runnable () {
            public void run() {
                Toast.makeText(activity, msg, Toast.LENGTH_LONG).show();
            }
        });

        // Wait to show the error.
        synchronized (activity) {
            try {
                activity.wait(1000);
            } catch (InterruptedException e) {
            }
        }
    }

    protected static void recursiveDelete(File f) {
        if (f.isDirectory()) {
            for (File r : f.listFiles()) {
                recursiveDelete(r);
            }
        }
        f.delete();
    }

    public static void unpackAsset(
        Context ctx,
        final String resource,
        File target,
        boolean cleanup_on_version_update) {

        Log.v(TAG, "Unpacking " + resource + " " + target.getName());

        // The version of data in memory and on disk.
        String dataVersion = getResourceString(ctx, resource + "_version");
        String diskVersion = null;

        Log.v(TAG, "Data version is " + dataVersion);

        // If no version, no unpacking is necessary.
        if (dataVersion == null) {
            return;
        }

        // Check the current disk version, if any.
        String filesDir = target.getAbsolutePath();
        String diskVersionFn = filesDir + "/" + resource + ".version";

        try {
            byte buf[] = new byte[64];
            InputStream is = new FileInputStream(diskVersionFn);
            int len = is.read(buf);
            diskVersion = new String(buf, 0, len);
            is.close();
        } catch (Exception e) {
            diskVersion = "";
        }

        // If the disk data is out of date, extract it and write the version file.
        if (! dataVersion.equals(diskVersion)) {
            Log.v(TAG, "Extracting " + resource + " assets.");

            if (cleanup_on_version_update) {
                recursiveDelete(target);
            }
            target.mkdirs();

            AssetExtract ae = new AssetExtract(ctx);
            if (!ae.extractTar(resource + ".tar", target.getAbsolutePath(), "private")) {
                String msg = "Could not extract " + resource + " data.";
                if (ctx instanceof Activity) {
                    toastError((Activity)ctx, msg);
                } else {
                    Log.v(TAG, msg);
                }
            }

            try {
                // Write .nomedia.
                new File(target, ".nomedia").createNewFile();

                // Write version file.
                FileOutputStream os = new FileOutputStream(diskVersionFn);
                os.write(dataVersion.getBytes());
                os.close();
            } catch (Exception e) {
                Log.w(TAG, e);
            }
        }
    }

    public static void unpackPyBundle(
        Context ctx,
        final String resource,
        File target,
        boolean cleanup_on_version_update) {

        Log.v(TAG, "Unpacking " + resource + " " + target.getName());

        // The version of data in memory and on disk.
        String dataVersion = getResourceString(ctx, "private_version");
        String diskVersion = null;

        Log.v(TAG, "Data version is " + dataVersion);

        // If no version, no unpacking is necessary.
        if (dataVersion == null) {
            return;
        }

        // Check the current disk version, if any.
        String filesDir = target.getAbsolutePath();
        String diskVersionFn = filesDir + "/" + "libpybundle" + ".version";

        try {
            byte buf[] = new byte[64];
            InputStream is = new FileInputStream(diskVersionFn);
            int len = is.read(buf);
            diskVersion = new String(buf, 0, len);
            is.close();
        } catch (Exception e) {
            diskVersion = "";
        }

        if (! dataVersion.equals(diskVersion)) {
            // If the disk data is out of date, extract it and write the version file.
            Log.v(TAG, "Extracting " + resource + " assets.");

            if (cleanup_on_version_update) {
                recursiveDelete(target);
            }
            target.mkdirs();

            AssetExtract ae = new AssetExtract(ctx);
            if (!ae.extractTar(resource + ".so", target.getAbsolutePath(), "pybundle")) {
                String msg = "Could not extract " + resource + " data.";
                if (ctx instanceof Activity) {
                    toastError((Activity)ctx, msg);
                } else {
                    Log.v(TAG, msg);
                }
            }

            try {
                // Write version file.
                FileOutputStream os = new FileOutputStream(diskVersionFn);
                os.write(dataVersion.getBytes());
                os.close();
            } catch (Exception e) {
                Log.w(TAG, e);
            }
        }
    }
}
