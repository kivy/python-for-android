package org.kivy.android;

import android.os.Build;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.os.Bundle;
import android.os.Process;
import android.app.Notification;
import android.app.PendingIntent;
import android.util.Log;
import java.io.File;

import org.kivy.android.PythonUtil;

import org.renpy.android.Hardware;

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
    private String androidUnpack;
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
        androidUnpack = extras.getString("androidUnpack");
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

        Notification notification;
        Context context = getApplicationContext();
        Intent contextIntent = new Intent(context, PythonActivity.class);
        PendingIntent pIntent = PendingIntent.getActivity(context, 0, contextIntent,
            PendingIntent.FLAG_UPDATE_CURRENT);
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.HONEYCOMB) {
            notification = new Notification(
                context.getApplicationInfo().icon, serviceTitle, System.currentTimeMillis());
            try {
                // prevent using NotificationCompat, this saves 100kb on apk
                Method func = notification.getClass().getMethod(
                    "setLatestEventInfo", Context.class, CharSequence.class,
                    CharSequence.class, PendingIntent.class);
                func.invoke(notification, context, serviceTitle, serviceDescription, pIntent);
            } catch (NoSuchMethodException | IllegalAccessException |
                     IllegalArgumentException | InvocationTargetException e) {
            }
        } else {
            Notification.Builder builder = new Notification.Builder(context);
            builder.setContentTitle(serviceTitle);
            builder.setContentText(serviceDescription);
            builder.setContentIntent(pIntent);
            builder.setSmallIcon(context.getApplicationInfo().icon);
            notification = builder.build();
        }
        startForeground(1, notification);
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
        String app_root =  getFilesDir().getAbsolutePath() + "/app";
        File app_root_file = new File(app_root);
        PythonUtil.loadLibraries(app_root_file);
        nativeStart(
            androidPrivate, androidArgument,
            serviceEntrypoint, pythonName,
            pythonHome, pythonPath,
            pythonServiceArgument);
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
    public static native void nativeStart(
            String androidPrivate, String androidArgument,
            String serviceEntrypoint, String pythonName,
            String pythonHome, String pythonPath,
            String pythonServiceArgument);
}
