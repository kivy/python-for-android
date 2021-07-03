package org.kivy.android;

import android.app.Notification;
import android.content.Intent;
import android.app.PendingIntent;

import android.app.Service;
import android.content.Context;
import android.os.Process;
import android.util.Log;

//imports for channel definition
import android.os.Build;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;

import android.app.NotificationManager;
import android.app.NotificationChannel;
import android.graphics.Color;

import java.io.File;

import org.kivy.android.PythonUtil;


public abstract class PythonBoundService extends Service implements Runnable {
    private static final String TAG = "python bound service";

    // Thread for Python code
    private Thread pythonThread = null;

    // Application root directory
    private String appRoot;

    // Python environment variables
    private String androidPrivate;
    private String androidArgument;
    private String pythonName;
    private String pythonHome;
    private String pythonPath;
    private String workerEntrypoint;

    // Argument to pass to Python code,
    private String pythonServiceArgument;
    public static PythonBoundService mService = null;

    public void setPythonName(String value) {
        Log.d(TAG, "setPythonName()");

        pythonName = value;
    }

    public void setWorkerEntrypoint(String value) {
        Log.d(TAG, "setWorkerEntrypoint()");

        workerEntrypoint = value;
    }

    public void startPythonThread() {
        Log.d(TAG, "startPythonThread()");

        pythonThread = new Thread(this);
        pythonThread.start();
    }

    @Override
    public void onCreate() {
        super.onCreate();
        this.mService = this;

        Log.d(TAG, "onCreate()");

        Context context = getApplicationContext();
        appRoot = PythonUtil.getAppRoot(context);

        androidPrivate = appRoot;
        androidArgument = appRoot;
        pythonHome = appRoot;
        pythonPath = appRoot + ":" + appRoot + "/lib";

        pythonServiceArgument = "";

        File appRootFile = new File(appRoot);

        Log.d(TAG, "unpack Data");

        PythonUtil.unpackData(context, "private", appRootFile, false);

        Log.d(TAG, "data unpacked");
    }

    @Override
    public void onDestroy() {
        super.onDestroy();

        Log.d(TAG, "onDestroy()");

        pythonThread = null;
        Process.killProcess(Process.myPid());
    }

    @Override
    public void run() {
        Log.d(TAG, "run()");

        File appRootFile = new File(appRoot);

        PythonUtil.loadLibraries(
            appRootFile,
            new File(getApplicationContext().getApplicationInfo().nativeLibraryDir)
        );

        Log.d(TAG, "Call native start");

        nativeStart(
            androidPrivate, androidArgument,
            workerEntrypoint, pythonName,
            pythonHome, pythonPath,
            pythonServiceArgument
        );

        this.mService = this;

        Log.d(TAG, "Python thread terminating");
    }

    // Native part
    public static native void nativeStart(
        String androidPrivate, String androidArgument,
        String workerEntrypoint, String pythonName,
        String pythonHome, String pythonPath,
        String pythonServiceArgument
    );

    /**
    * change the bound service to foreground service
    * automatically creates notification
    * @param serviceTitle: this text appears as notification title
    * @param serviceDescription: this text as notification description
    */
    public void doStartForeground(String serviceTitle, String serviceDescription) {
        Notification notification;
        Context context = getApplicationContext();
        Intent contextIntent = new Intent(context, PythonActivity.class);
        PendingIntent pIntent = PendingIntent.getActivity(context, 0, contextIntent,
            PendingIntent.FLAG_UPDATE_CURRENT);

        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
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
            // for android 8+ we need to create our own channel
            // https://stackoverflow.com/questions/47531742/startforeground-fail-after-upgrade-to-android-8-1
            String NOTIFICATION_CHANNEL_ID = "org.kivy.p4a";    //TODO: make this configurable
            String channelName = "Background Service";                //TODO: make this configurable
            NotificationChannel chan = new NotificationChannel(NOTIFICATION_CHANNEL_ID, channelName,
                NotificationManager.IMPORTANCE_NONE);

            chan.setLightColor(Color.BLUE);
            chan.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);
            NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            manager.createNotificationChannel(chan);

            Notification.Builder builder = new Notification.Builder(context, NOTIFICATION_CHANNEL_ID);
            builder.setContentTitle(serviceTitle);
            builder.setContentText(serviceDescription);
            builder.setContentIntent(pIntent);
            builder.setSmallIcon(context.getApplicationInfo().icon);
            notification = builder.build();
        }
        startForeground(getServiceId(), notification);
    }

    int getServiceId() {
        return 1;
    }
}
