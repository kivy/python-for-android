package org.kivy.android;

import java.io.InputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.File;

import android.app.Activity;
import android.util.Log;
import android.widget.Toast;

import org.renpy.android.ResourceManager;
import org.renpy.android.AssetExtract;


public class PythonActivityUtil {
	private static final String TAG = "pythonactivityutil";
    private ResourceManager mResourceManager = null;
    private Activity mActivity = null;


    public PythonActivityUtil(Activity activity, ResourceManager resourceManager) {
        this.mActivity = activity;
        this.mResourceManager = resourceManager;
    }

    /**
     * Show an error using a toast. (Only makes sense from non-UI threads.)
     */
    private void toastError(final String msg) {
        mActivity.runOnUiThread(new Runnable () {
            public void run() {
                Toast.makeText(mActivity, msg, Toast.LENGTH_LONG).show();
            }
        });

        // Wait to show the error.
        synchronized (mActivity) {
            try {
                mActivity.wait(1000);
            } catch (InterruptedException e) {
            }
        }
    }

    private void recursiveDelete(File f) {
        if (f.isDirectory()) {
            for (File r : f.listFiles()) {
                recursiveDelete(r);
            }
        }
        f.delete();
    }

    public void unpackData(final String resource, File target) {

        Log.v(TAG, "UNPACKING!!! " + resource + " " + target.getName());

        // The version of data in memory and on disk.
        String dataVersion = mResourceManager.getString(resource + "_version");
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

            recursiveDelete(target);
            target.mkdirs();

            AssetExtract ae = new AssetExtract(mActivity);
            if (!ae.extractTar(resource + ".mp3", target.getAbsolutePath())) {
                toastError("Could not extract " + resource + " data.");
            }

            try {
                // Write .nomedia.
                new File(target, ".nomedia").createNewFile();

                // Write version file.
                FileOutputStream os = new FileOutputStream(diskVersionFn);
                os.write(dataVersion.getBytes());
                os.close();
            } catch (Exception e) {
                Log.w("python", e);
            }
        }
    }

}
