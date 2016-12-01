
package org.kivy.android;

import java.io.InputStream;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.File;
import java.io.IOException;
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
import android.widget.ImageView;
import java.io.InputStream;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;

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

    public String getAppRoot() {
        String app_root =  getFilesDir().getAbsolutePath() + "/app";
        return app_root;
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.v(TAG, "My oncreate running");
        resourceManager = new ResourceManager(this);
        this.showLoadingScreen();
        File app_root_file = new File(getAppRoot());

        Log.v(TAG, "Ready to unpack");
        unpackData("private", app_root_file);

        Log.v(TAG, "About to do super onCreate");
        super.onCreate(savedInstanceState);
        Log.v(TAG, "Did super onCreate");

        this.mActivity = this;
        this.showLoadingScreen();
        

        String app_root_dir = getAppRoot();
        String mFilesDirectory = mActivity.getFilesDir().getAbsolutePath();
        Log.v(TAG, "Setting env vars for start.c and Python to use");
        SDLActivity.nativeSetEnv("ANDROID_PRIVATE", mFilesDirectory);
        SDLActivity.nativeSetEnv("ANDROID_ARGUMENT", app_root_dir);
        SDLActivity.nativeSetEnv("ANDROID_APP_PATH", app_root_dir);
        SDLActivity.nativeSetEnv("ANDROID_ENTRYPOINT", "main.pyo");
        SDLActivity.nativeSetEnv("PYTHONHOME", app_root_dir);
        SDLActivity.nativeSetEnv("PYTHONPATH", app_root_dir + ":" + app_root_dir + "/lib");
        SDLActivity.nativeSetEnv("PYTHONOPTIMIZE", "2");

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
        String app_root = new String(getAppRoot());
        File app_root_file = new File(app_root);
        PythonUtil.loadLibraries(app_root_file);
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
        String app_root_dir = PythonActivity.mActivity.getAppRoot();
        serviceIntent.putExtra("androidPrivate", argument);
        serviceIntent.putExtra("androidArgument", app_root_dir);
        serviceIntent.putExtra("serviceEntrypoint", "service/main.pyo");
        serviceIntent.putExtra("pythonHome", app_root_dir);
        serviceIntent.putExtra("pythonPath", app_root_dir + ":" + app_root_dir + "/lib");
        serviceIntent.putExtra("serviceTitle", serviceTitle);
        serviceIntent.putExtra("serviceDescription", serviceDescription);
        serviceIntent.putExtra("pythonServiceArgument", pythonServiceArgument);
        PythonActivity.mActivity.startService(serviceIntent);
    }

    public static void stop_service() {
        Intent serviceIntent = new Intent(PythonActivity.mActivity, PythonService.class);
        PythonActivity.mActivity.stopService(serviceIntent);
    }

    /** Loading screen implementation
    * keepActive() is a method plugged in pollInputDevices in SDLActivity.
    * Once it's called twice, the loading screen will be removed.
    * The first call happen as soon as the window is created, but no image has been
    * displayed first. My tests showed that we can wait one more. This might delay
    * the real available of few hundred milliseconds.
    * The real deal is to know if a rendering has already happen. The previous
    * python-for-android and kivy was having something for that, but this new version
    * is not compatible, and would require a new kivy version.
    * In case of, the method PythonActivty.mActivity.removeLoadingScreen() can be called.
    */
    public static ImageView mImageView = null;
    int mLoadingCount = 2;

    @Override
    public void keepActive() {
      if (this.mLoadingCount > 0) {
        this.mLoadingCount -= 1;
        if (this.mLoadingCount == 0) {
          this.removeLoadingScreen();
        }
      }
    }

    public void removeLoadingScreen() {
      runOnUiThread(new Runnable() {
        public void run() {
          if (PythonActivity.mImageView != null && 
        		  PythonActivity.mImageView.getParent() != null) {
            ((ViewGroup)PythonActivity.mImageView.getParent()).removeView(
            PythonActivity.mImageView);
            PythonActivity.mImageView = null;
          }
        }
      });
    }


    protected void showLoadingScreen() {
      // load the bitmap
      // 1. if the image is valid and we don't have layout yet, assign this bitmap
      // as main view.
      // 2. if we have a layout, just set it in the layout.
      // 3. If we have an mImageView already, then do nothing because it will have
      // already been made the content view or added to the layout.

      if (mImageView == null) {
        int presplashId = this.resourceManager.getIdentifier("presplash", "drawable");
        InputStream is = this.getResources().openRawResource(presplashId);
        Bitmap bitmap = null;
        try {
          bitmap = BitmapFactory.decodeStream(is);
        } finally {
          try {
            is.close();
          } catch (IOException e) {};
        }

        mImageView = new ImageView(this);
        mImageView.setImageBitmap(bitmap);

        /*
	 * Set the presplash loading screen background color
         * https://developer.android.com/reference/android/graphics/Color.html
         * Parse the color string, and return the corresponding color-int.
         * If the string cannot be parsed, throws an IllegalArgumentException exception.
         * Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
         * 'red', 'blue', 'green', 'black', 'white', 'gray', 'cyan', 'magenta', 'yellow',
         * 'lightgray', 'darkgray', 'grey', 'lightgrey', 'darkgrey', 'aqua', 'fuchsia',
         * 'lime', 'maroon', 'navy', 'olive', 'purple', 'silver', 'teal'.
         */
        String backgroundColor = resourceManager.getString("presplash_color");
        if (backgroundColor != null) {
          try {
            mImageView.setBackgroundColor(Color.parseColor(backgroundColor));
          } catch (IllegalArgumentException e) {}
        }   
        mImageView.setLayoutParams(new ViewGroup.LayoutParams(
        ViewGroup.LayoutParams.FILL_PARENT,
        ViewGroup.LayoutParams.FILL_PARENT));
        mImageView.setScaleType(ImageView.ScaleType.FIT_CENTER);

    }

    if (mLayout == null) {
      setContentView(mImageView);
    } else if (PythonActivity.mImageView.getParent() == null){
      mLayout.addView(mImageView);
    }

    }

}
