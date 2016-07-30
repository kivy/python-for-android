package org.kivy.android;

import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.os.Bundle;
import android.os.Process;
import android.support.v4.app.NotificationCompat;
import android.util.Log;

public abstract class PythonService extends Service implements Runnable {
    private static String TAG = PythonService.class.getSimpleName();

    /**
     * Intent that started the service
     */
    private Intent startIntent = null;

    private Thread pythonThread = null;

    // Python environment variables
    private String androidPrivate;
    private String androidArgument;
    private String pythonName;
    private String pythonHome;
    private String pythonPath;
    private String serviceEntrypoint;
    private String pythonServiceArgument;

    public int getStartType() {
        return START_NOT_STICKY;
    }

    public boolean getStartForeground() {
        return false;
    }

    public boolean getAutoRestart() {
        return false;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public void onCreate() {
        Log.v(TAG, "Device: " + android.os.Build.DEVICE);
        Log.v(TAG, "Model: " + android.os.Build.MODEL);
        AssetExtract.extractAsset(getApplicationContext(), "private.mp3", getFilesDir());
        super.onCreate();
    }

    /**
     * {@inheritDoc}
     */
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

        Log.v(TAG, "Starting Python thread");
        pythonThread = new Thread(this);
        pythonThread.start();

        if (getStartForeground()) {
            doStartForeground(extras);
        }

        return getStartType();
    }

    protected void doStartForeground(Bundle extras) {
        Context appContext = getApplicationContext();
        ApplicationInfo appInfo = appContext.getApplicationInfo();

        String serviceTitle = extras.getString("serviceTitle", TAG);
        String serviceDescription = extras.getString("serviceDescription", "");
        int serviceIconId = extras.getInt("serviceIconId", appInfo.icon);

        NotificationCompat.Builder builder =
                new NotificationCompat.Builder(this)
                        .setSmallIcon(serviceIconId)
                        .setContentTitle(serviceTitle)
                        .setContentText(serviceDescription);

        int NOTIFICATION_ID = 1;

        Intent targetIntent = new Intent(this, MainActivity.class);
        PendingIntent contentIntent = PendingIntent.getActivity(this, 0, targetIntent, PendingIntent.FLAG_UPDATE_CURRENT);
        builder.setContentIntent(contentIntent);

        startForeground(NOTIFICATION_ID, builder.build());
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public void onDestroy() {
        super.onDestroy();
        pythonThread = null;
        if (getAutoRestart() && startIntent != null) {
            Log.v(TAG, "Service restart requested");
            startService(startIntent);
        }
        Process.killProcess(Process.myPid());
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public void run() {
        PythonUtil.loadLibraries(getFilesDir());
        nativeStart(androidPrivate, androidArgument, serviceEntrypoint, pythonName, pythonHome,
                pythonPath, pythonServiceArgument);
        stopSelf();
    }

    /**
     * @param androidPrivate        Directory for private files
     * @param androidArgument       Android path
     * @param serviceEntrypoint     Python file to execute first
     * @param pythonName            Python name
     * @param pythonHome            Python home
     * @param pythonPath            Python path
     * @param pythonServiceArgument Argument to pass to Python code
     */
    public static native void nativeStart(String androidPrivate, String androidArgument,
                                          String serviceEntrypoint, String pythonName,
                                          String pythonHome, String pythonPath,
                                          String pythonServiceArgument);
}
