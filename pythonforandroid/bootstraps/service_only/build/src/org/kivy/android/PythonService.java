package org.kivy.android;

import android.app.Service;
import android.content.Intent;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Process;
import android.util.Log;

public class PythonService extends Service implements Runnable {
    private static String TAG = PythonService.class.getSimpleName();

    public static PythonService mService = null;
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

    private boolean autoRestartService = false;

    public void setAutoRestartService(boolean restart) {
        autoRestartService = restart;
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public IBinder onBind(Intent intent) {
        return null;
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

	/**
     * {@inheritDoc}
     */
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

    /**
     * {@inheritDoc}
     */
    @Override
    public void run() {
        PythonUtil.loadLibraries(getFilesDir());
        mService = this;
        nativeStart(androidPrivate, androidArgument, serviceEntrypoint,
                pythonName, pythonHome, pythonPath, pythonServiceArgument);
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
    public static native void nativeStart(String androidPrivate,
                                          String androidArgument, String serviceEntrypoint,
                                          String pythonName, String pythonHome, String pythonPath,
                                          String pythonServiceArgument);
}
