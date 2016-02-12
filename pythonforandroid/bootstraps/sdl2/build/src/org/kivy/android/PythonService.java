package org.kivy.android;

import android.app.Service;
import android.os.IBinder;
import android.os.Bundle;
import android.content.Intent;
import android.content.Context;
import android.util.Log;
import android.app.Notification;
import android.app.PendingIntent;
import android.os.Process;

import org.kivy.android.PythonUtil;

import org.renpy.android.Hardware;


public class PythonService extends Service implements Runnable {

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
    public static Service mService = null;

    public boolean canDisplayNotification() {
        return true;
    }

    @Override
    public IBinder onBind(Intent arg0) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (pythonThread != null) {
            Log.v("python service", "service exists, do not start again");
            return START_NOT_STICKY;
        }

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

        doStartForeground(extras);

        return START_NOT_STICKY;
    }

    protected void doStartForeground(Bundle extras) {
        if (canDisplayNotification()) {
            String serviceTitle = extras.getString("serviceTitle");
            String serviceDescription = extras.getString("serviceDescription");

            Context context = getApplicationContext();
            Notification notification = new Notification(context.getApplicationInfo().icon,
                serviceTitle, System.currentTimeMillis());
            Intent contextIntent = new Intent(context, PythonActivity.class);
            PendingIntent pIntent = PendingIntent.getActivity(context, 0, contextIntent,
                PendingIntent.FLAG_UPDATE_CURRENT);
            notification.setLatestEventInfo(context, serviceTitle, serviceDescription, pIntent);
            startForeground(1, notification);
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        pythonThread = null;
        Process.killProcess(Process.myPid());
    }

    @Override
    public void run(){
        PythonUtil.loadLibraries(getFilesDir());
        this.mService = this;
        nativeStart(
            androidPrivate, androidArgument,
            serviceEntrypoint, pythonName,
            pythonHome, pythonPath,
            pythonServiceArgument);
        stopSelf();
    }

    // Native part
    public static native void nativeStart(
            String androidPrivate, String androidArgument,
            String serviceEntrypoint, String pythonName,
            String pythonHome, String pythonPath,
            String pythonServiceArgument);
}
