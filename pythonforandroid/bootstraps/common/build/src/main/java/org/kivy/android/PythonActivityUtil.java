package org.kivy.android;

import android.app.Activity;
import android.util.Log;
import android.widget.Toast;

import org.renpy.android.ResourceManager;


public class PythonActivityUtil {

    // XXX: This class is no longer used in any of p4a bootstraps.
    //      Keep it here for B/C or remove?

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

    public void unpackData(final String resource, File target) {
        Log.d(TAG, "B/C call of ``PythonActivityUtil.unpackData``. Use ``PythonUtil.unpackData`` instead.");
        PythonUtil.unpackData(mActivity, resource, target, true);
    }
}
