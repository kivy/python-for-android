
package org.kivy.android;

import java.io.InputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.File;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.ArrayList;

import android.view.ViewGroup;
import android.view.SurfaceView;
import android.app.Activity;
import android.content.Intent;
import android.util.Log;
import android.widget.Toast;
import android.os.Bundle;
import android.os.PowerManager;
import android.graphics.PixelFormat;
import android.view.SurfaceHolder;
import android.content.Context;
import android.content.pm.PackageManager;
import android.content.pm.ApplicationInfo;
import android.content.Intent;

import org.libsdl.app.SDLActivity;

import org.kivy.android.PythonUtil;

import org.renpy.android.ResourceManager;
import org.renpy.android.AssetExtract;


public class PythonActivity extends SDLActivity {
    private static final String TAG = "PythonActivity";

    public static PythonActivity mActivity = null;
    
    private ResourceManager resourceManager = null;
    private Bundle mMetaData = null;
    private PowerManager.WakeLock mWakeLock = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.v(TAG, "My oncreate running");
        resourceManager = new ResourceManager(this);

        Log.v(TAG, "Ready to unpack");
        unpackData("private", getFilesDir());

        Log.v(TAG, "About to do super onCreate");
        super.onCreate(savedInstanceState);
        Log.v(TAG, "Did super onCreate");
        
        this.mActivity = this;
        
        String mFilesDirectory = mActivity.getFilesDir().getAbsolutePath();
        Log.v(TAG, "Setting env vars for start.c and Python to use");
        SDLActivity.nativeSetEnv("ANDROID_PRIVATE", mFilesDirectory);
        SDLActivity.nativeSetEnv("ANDROID_ARGUMENT", mFilesDirectory);
        SDLActivity.nativeSetEnv("ANDROID_APP_PATH", mFilesDirectory);
        SDLActivity.nativeSetEnv("PYTHONHOME", mFilesDirectory);
        SDLActivity.nativeSetEnv("PYTHONPATH", mFilesDirectory + ":" + mFilesDirectory + "/lib");

        
        // nativeSetEnv("ANDROID_ARGUMENT", getFilesDir());

        try {
            Log.v(TAG, "Access to our meta-data...");
            this.mMetaData = this.mActivity.getPackageManager().getApplicationInfo(
                    this.mActivity.getPackageName(), PackageManager.GET_META_DATA).metaData;

            PowerManager pm = (PowerManager) this.mActivity.getSystemService(Context.POWER_SERVICE);
            if ( this.mMetaData.getInt("wakelock") == 1 ) {
                this.mWakeLock = pm.newWakeLock(PowerManager.SCREEN_BRIGHT_WAKE_LOCK, "Screen On");
            }
            if ( this.mMetaData.getInt("surface.transparent") != 0 ) {
                Log.v(TAG, "Surface will be transparent.");
                getSurface().setZOrderOnTop(true);
                getSurface().getHolder().setFormat(PixelFormat.TRANSPARENT);
            } else {
                Log.i(TAG, "Surface will NOT be transparent");
            }
        } catch (PackageManager.NameNotFoundException e) {
        }
    }
    
    public void loadLibraries() {
        PythonUtil.loadLibraries(getFilesDir());
    }
    
    public void recursiveDelete(File f) {
        if (f.isDirectory()) {
            for (File r : f.listFiles()) {
                recursiveDelete(r);
            }
        }
        f.delete();
    }

    /**
     * Show an error using a toast. (Only makes sense from non-UI
     * threads.)
     */
    public void toastError(final String msg) {

        final Activity thisActivity = this;

        runOnUiThread(new Runnable () {
            public void run() {
                Toast.makeText(thisActivity, msg, Toast.LENGTH_LONG).show();
            }
        });

        // Wait to show the error.
        synchronized (this) {
            try {
                this.wait(1000);
            } catch (InterruptedException e) {
            }
        }
    }
    
    public void unpackData(final String resource, File target) {
        
        Log.v(TAG, "UNPACKING!!! " + resource + " " + target.getName());
        
        // The version of data in memory and on disk.
        String data_version = resourceManager.getString(resource + "_version");
        String disk_version = null;
        
        Log.v(TAG, "Data version is " + data_version);

        // If no version, no unpacking is necessary.
        if (data_version == null) {
            return;
        }

        // Check the current disk version, if any.
        String filesDir = target.getAbsolutePath();
        String disk_version_fn = filesDir + "/" + resource + ".version";

        try {
            byte buf[] = new byte[64];
            InputStream is = new FileInputStream(disk_version_fn);
            int len = is.read(buf);
            disk_version = new String(buf, 0, len);
            is.close();
        } catch (Exception e) {
            disk_version = "";
        }

        // If the disk data is out of date, extract it and write the
        // version file.
        // if (! data_version.equals(disk_version)) {
        if (! data_version.equals(disk_version)) {
            Log.v(TAG, "Extracting " + resource + " assets.");

            recursiveDelete(target);
            target.mkdirs();

            AssetExtract ae = new AssetExtract(this);
            if (!ae.extractTar(resource + ".mp3", target.getAbsolutePath())) {
                toastError("Could not extract " + resource + " data.");
            }

            try {
                // Write .nomedia.
                new File(target, ".nomedia").createNewFile();

                // Write version file.
                FileOutputStream os = new FileOutputStream(disk_version_fn);
                os.write(data_version.getBytes());
                os.close();
            } catch (Exception e) {
                Log.w("python", e);
            }
        }
    }
    
    public static ViewGroup getLayout() {
        return   mLayout;
    }

    public static SurfaceView getSurface() {
        return   mSurface;
    }

    //----------------------------------------------------------------------------
    // Listener interface for onNewIntent
    //

    public interface NewIntentListener {
        void onNewIntent(Intent intent);
    }

    private List<NewIntentListener> newIntentListeners = null;

    public void registerNewIntentListener(NewIntentListener listener) {
        if ( this.newIntentListeners == null )
            this.newIntentListeners = Collections.synchronizedList(new ArrayList<NewIntentListener>());
        this.newIntentListeners.add(listener);
    }

    public void unregisterNewIntentListener(NewIntentListener listener) {
        if ( this.newIntentListeners == null )
            return;
        this.newIntentListeners.remove(listener);
    }

    @Override
    protected void onNewIntent(Intent intent) {
        if ( this.newIntentListeners == null )
            return;
        this.onResume();
        synchronized ( this.newIntentListeners ) {
            Iterator<NewIntentListener> iterator = this.newIntentListeners.iterator();
            while ( iterator.hasNext() ) {
                (iterator.next()).onNewIntent(intent);
            }
        }
    }

    //----------------------------------------------------------------------------
    // Listener interface for onActivityResult
    //

    public interface ActivityResultListener {
        void onActivityResult(int requestCode, int resultCode, Intent data);
    }

    private List<ActivityResultListener> activityResultListeners = null;

    public void registerActivityResultListener(ActivityResultListener listener) {
        if ( this.activityResultListeners == null )
            this.activityResultListeners = Collections.synchronizedList(new ArrayList<ActivityResultListener>());
        this.activityResultListeners.add(listener);
    }

    public void unregisterActivityResultListener(ActivityResultListener listener) {
        if ( this.activityResultListeners == null )
            return;
        this.activityResultListeners.remove(listener);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent intent) {
        if ( this.activityResultListeners == null )
            return;
        this.onResume();
        synchronized ( this.activityResultListeners ) {
            Iterator<ActivityResultListener> iterator = this.activityResultListeners.iterator();
            while ( iterator.hasNext() )
                (iterator.next()).onActivityResult(requestCode, resultCode, intent);
        }
    }

	public static void start_service(String serviceTitle, String serviceDescription,
                String pythonServiceArgument) {
        Intent serviceIntent = new Intent(PythonActivity.mActivity, PythonService.class);
        String argument = PythonActivity.mActivity.getFilesDir().getAbsolutePath();
        String filesDirectory = argument;
        serviceIntent.putExtra("androidPrivate", argument);
        serviceIntent.putExtra("androidArgument", filesDirectory);
        serviceIntent.putExtra("pythonHome", argument);
        serviceIntent.putExtra("pythonPath", argument + ":" + filesDirectory + "/lib");
        serviceIntent.putExtra("serviceTitle", serviceTitle);
        serviceIntent.putExtra("serviceDescription", serviceDescription);
        serviceIntent.putExtra("pythonServiceArgument", pythonServiceArgument);
        PythonActivity.mActivity.startService(serviceIntent);
    }

    public static void stop_service() {
        Intent serviceIntent = new Intent(PythonActivity.mActivity, PythonService.class);
        PythonActivity.mActivity.stopService(serviceIntent);
    }
}
