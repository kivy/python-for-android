package org.kivy.android;

import android.app.Service;
import android.content.Context;
import android.os.Process;
import android.util.Log;

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
        Log.d(TAG, "onCreate()");

        super.onCreate();

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
        Log.d(TAG, "onDestroy()");

        super.onDestroy();
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

        Log.d(TAG, "Python thread terminating");
    }

    // Native part
    public static native void nativeStart(
        String androidPrivate, String androidArgument,
        String workerEntrypoint, String pythonName,
        String pythonHome, String pythonPath,
        String pythonServiceArgument
    );
}
