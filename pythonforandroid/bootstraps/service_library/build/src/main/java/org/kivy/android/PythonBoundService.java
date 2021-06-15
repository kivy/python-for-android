package org.kivy.android;

import android.app.Service;
import android.content.Context;
import android.os.Process;
import android.util.Log;

import java.io.File;

import org.kivy.android.PythonUtil;


public abstract class PythonBoundService extends Service implements Runnable {
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

    public void setPythonName(String value) {
        pythonName = value;
    }

    public void setWorkerEntrypoint(String value) {
        workerEntrypoint = value;
    }

    public void startPythonThread() {
        pythonThread = new Thread(this);
        pythonThread.start();
    }

    @Override
    public void onCreate() {
        super.onCreate();

        Context context = getApplicationContext();
        appRoot = PythonUtil.getAppRoot(context);

        androidPrivate = appRoot;
        androidArgument = appRoot;
        pythonHome = appRoot;
        pythonPath = appRoot + ":" + appRoot + "/lib";

        File appRootFile = new File(appRoot);
        PythonUtil.unpackData(context, "private", appRootFile, false);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        pythonThread = null;
        Process.killProcess(Process.myPid());
    }

    @Override
    public void run() {
        File appRootFile = new File(appRoot);

        PythonUtil.loadLibraries(
            appRootFile,
            new File(getApplicationContext().getApplicationInfo().nativeLibraryDir)
        );

        nativeStart(
            androidPrivate, androidArgument,
            workerEntrypoint, pythonName,
            pythonHome, pythonPath
        );
        Log.d("python bound service", "Python thread terminating");
    }

    // Native part
    public static native void nativeStart(
        String androidPrivate, String androidArgument,
        String workerEntrypoint, String pythonName,
        String pythonHome, String pythonPath
    );
}
