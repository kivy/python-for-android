package org.kivy.android;

import android.app.Service;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Process;
import android.util.Log;

import org.renpy.android.AssetExtract;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;

public class PythonService extends Service implements Runnable {
    private static String TAG = "PythonService";

    // Thread for Python code
    private Thread pythonThread = null;

    // Python environment variables
    private String androidPrivate;
    private String androidArgument;
    private String pythonName;
    private String pythonHome;
    private String pythonPath;
    private String serviceEntrypoint;

    // Argument to pass to Python code,
    private String pythonServiceArgument;
    public static PythonService mService = null;
    private Intent startIntent = null;

    private boolean autoRestartService = false;

    public void setAutoRestartService(boolean restart) {
        autoRestartService = restart;
    }

    public boolean canDisplayNotification() {
        return true;
    }

    public int startType() {
        return START_NOT_STICKY;
    }

    @Override
    public IBinder onBind(Intent arg0) {
        return null;
    }

    @Override
    public void onCreate() {
        Log.v(TAG, "Device: " + android.os.Build.DEVICE);
        Log.v(TAG, "Model: " + android.os.Build.MODEL);
        unpackData("private", getFilesDir());
        super.onCreate();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (pythonThread != null) {
            Log.v(TAG, "Service exists, do not start again");
            return START_NOT_STICKY;
        }

        startIntent = intent;
        Bundle extras = intent.getExtras();
        androidPrivate = extras.getString("androidPrivate");
        androidArgument = extras.getString("androidArgument");
        serviceEntrypoint = extras.getString("serviceEntrypoint");
        pythonName = extras.getString("pythonName");
        pythonHome = extras.getString("pythonHome");
        pythonPath = extras.getString("pythonPath");
        pythonServiceArgument = extras.getString("pythonServiceArgument");

        pythonThread = new Thread(this);
        pythonThread.start();

		if (canDisplayNotification()) {
			doStartForeground(extras);
		}

        return startType();
    }

	protected void doStartForeground(Bundle extras) {
		String serviceTitle = extras.getString("serviceTitle");
		String serviceDescription = extras.getString("serviceDescription");

		Context context = getApplicationContext();
		Notification notification = new Notification(
				context.getApplicationInfo().icon, serviceTitle,
				System.currentTimeMillis());
		Intent contextIntent = new Intent(context, PythonActivity.class);
		PendingIntent pIntent = PendingIntent.getActivity(context, 0,
				contextIntent, PendingIntent.FLAG_UPDATE_CURRENT);
		notification.setLatestEventInfo(context, serviceTitle,
				serviceDescription, pIntent);
		startForeground(1, notification);
	}

    @Override
    public void onDestroy() {
        super.onDestroy();
        pythonThread = null;
        if (autoRestartService && startIntent != null) {
            Log.v(TAG, "Service restart requested");
            startService(startIntent);
        }
        Process.killProcess(Process.myPid());
    }

    @Override
    public void run() {
        PythonUtil.loadLibraries(getFilesDir());
        mService = this;
        nativeStart(androidPrivate, androidArgument, serviceEntrypoint,
                pythonName, pythonHome, pythonPath, pythonServiceArgument);
        stopSelf();
    }

    public void recursiveDelete(File f) {
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
        String data_version = null;
        String disk_version = null;

        try {
            PackageManager manager = this.getPackageManager();
            PackageInfo info = manager.getPackageInfo(this.getPackageName(), 0);
            data_version = info.versionName;

            Log.v(TAG, "Data version is " + data_version);
        } catch (PackageManager.NameNotFoundException e) {
            Log.w(TAG, "Data version not found of " + resource + " data.");
        }

        // If no version, no unpacking is necessary.
        if (data_version == null) {
            return;
        }

        // Check the current disk version, if any.
        String filesDir = target.getAbsolutePath();
        String disk_version_fn = filesDir + "/" + resource + ".version";

        try {
            byte buf[] = new byte[64];
            FileInputStream is = new FileInputStream(disk_version_fn);
            int len = is.read(buf);
            disk_version = new String(buf, 0, len);
            is.close();
        } catch (Exception e) {
            disk_version = "";
        }

        // If the disk data is out of date, extract it and write the version
        // file.
        if (!data_version.equals(disk_version)) {
            Log.v(TAG, "Extracting " + resource + " assets.");

            recursiveDelete(target);
            target.mkdirs();

            AssetExtract ae = new AssetExtract(this);
            if (!ae.extractTar(resource + ".mp3", target.getAbsolutePath())) {
                Log.e(TAG, "Could not extract " + resource + " data.");
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

    // Native part
    public static native void nativeStart(String androidPrivate,
                                          String androidArgument, String serviceEntrypoint,
                                          String pythonName, String pythonHome, String pythonPath,
                                          String pythonServiceArgument);
}
