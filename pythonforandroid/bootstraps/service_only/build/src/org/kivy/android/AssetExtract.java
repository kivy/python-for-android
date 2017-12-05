package org.kivy.android;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.res.AssetManager;
import android.util.Log;

import org.kamranzafar.jtar.TarEntry;
import org.kamranzafar.jtar.TarInputStream;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.zip.GZIPInputStream;

public class AssetExtract {
    private static String TAG = AssetExtract.class.getSimpleName();

    /**
     * @param parent File or directory to delete recursively
     */
    public static void recursiveDelete(File parent) {
        if (parent.isDirectory()) {
            for (File child : parent.listFiles()) {
                recursiveDelete(child);
            }
        }
        parent.delete();
    }

    public static void extractAsset(Context ctx, String assetName, File target) {
        Log.v(TAG, "Extract asset " + assetName + " to " + target.getAbsolutePath());

        // The version of data in memory and on disk.
        String packaged_version;
        String disk_version;

        try {
            PackageManager manager = ctx.getPackageManager();
            PackageInfo info = manager.getPackageInfo(ctx.getPackageName(), 0);
            packaged_version = info.versionName;

            Log.v(TAG, "Data version is " + packaged_version);
        } catch (PackageManager.NameNotFoundException e) {
            packaged_version = null;
        }
        // If no packaged data version, no unpacking is necessary.
        if (packaged_version == null) {
            Log.w(TAG, "Data version not found");
            return;
        }

        // Check the current disk version, if any.
        String filesDir = target.getAbsolutePath();
        String disk_version_fn = filesDir + "/" + assetName + ".version";

        try {
            byte buf[] = new byte[64];
            FileInputStream is = new FileInputStream(disk_version_fn);
            int len = is.read(buf);
            disk_version = new String(buf, 0, len);
            is.close();
        } catch (Exception e) {
            disk_version = "";
        }

        if (packaged_version.equals(disk_version)) {
            Log.v(TAG, "Disk data version equals packaged data version.");
            return;
        }

        recursiveDelete(target);
        target.mkdirs();

        if (!extractTar(ctx.getAssets(), assetName, target.getAbsolutePath())) {
            Log.e(TAG, "Could not extract " + assetName + " data.");
        }

        try {
            // Write .nomedia.
            new File(target, ".nomedia").createNewFile();

            // Write version file.
            FileOutputStream os = new FileOutputStream(disk_version_fn);
            os.write(packaged_version.getBytes());
            os.close();
        } catch (Exception ex) {
            Log.w(TAG, ex);
        }
    }

    public static boolean extractTar(AssetManager assets, String assetName, String target) {
        byte buf[] = new byte[1024 * 1024];

        InputStream assetStream = null;
        TarInputStream tis = null;

        try {
            assetStream = assets.open(assetName, AssetManager.ACCESS_STREAMING);
            tis = new TarInputStream(new BufferedInputStream(
                    new GZIPInputStream(new BufferedInputStream(assetStream,
                            8192)), 8192));
        } catch (IOException e) {
            Log.e(TAG, "opening up extract tar", e);
            return false;
        }

        while (true) {
            TarEntry entry = null;

            try {
                entry = tis.getNextEntry();
            } catch (java.io.IOException e) {
                Log.e(TAG, "extracting tar", e);
                return false;
            }

            if (entry == null) {
                break;
            }

            Log.v(TAG, "extracting " + entry.getName());

            if (entry.isDirectory()) {

                try {
                    new File(target + "/" + entry.getName()).mkdirs();
                } catch (SecurityException e) {
                    Log.e(TAG, "extracting tar", e);
                }

                continue;
            }

            OutputStream out = null;
            String path = target + "/" + entry.getName();

            try {
                out = new BufferedOutputStream(new FileOutputStream(path), 8192);
            } catch (FileNotFoundException e) {
                Log.e(TAG, "extracting tar", e);
            } catch (SecurityException e) {
                Log.e(TAG, "extracting tar", e);
            }

            if (out == null) {
                Log.e(TAG, "could not open " + path);
                return false;
            }

            try {
                while (true) {
                    int len = tis.read(buf);

                    if (len == -1) {
                        break;
                    }

                    out.write(buf, 0, len);
                }

                out.flush();
                out.close();
            } catch (java.io.IOException e) {
                Log.e(TAG, "extracting zip", e);
                return false;
            }
        }

        try {
            tis.close();
            assetStream.close();
        } catch (IOException e) {
            // pass
        }

        return true;
    }
}