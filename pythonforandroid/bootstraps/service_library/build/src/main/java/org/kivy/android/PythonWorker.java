package org.kivy.android;

import android.content.Context;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.concurrent.futures.CallbackToFutureAdapter.Completer;
import androidx.concurrent.futures.CallbackToFutureAdapter;
import androidx.work.ListenableWorker.Result;
// import androidx.work.ListenableWorker;
import androidx.work.multiprocess.RemoteListenableWorker;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

import com.google.common.util.concurrent.ListenableFuture;

import java.io.File;

import org.kivy.android.PythonUtil;

// public class PythonWorker extends ListenableWorker implements Runnable {
public class PythonWorker extends RemoteListenableWorker implements Runnable {
    // Completer for worker notification
    private Completer workCompleter = null;

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

    public PythonWorker(
        @NonNull Context context,
        @NonNull WorkerParameters params) {
        super(context, params);
        Log.d("RemoteListenableWorker", "PythonWorker constructor");

        appRoot = PythonUtil.getAppRoot(context);

        androidPrivate = appRoot;
        androidArgument = appRoot;
        pythonHome = appRoot;
        pythonPath = appRoot + ":" + appRoot + "/lib";

        pythonServiceArgument = "";

        File appRootFile = new File(appRoot);
        PythonUtil.unpackData(context, "private", appRootFile, false);
    }

    public void setPythonName(String value) {
        pythonName = value;
    }

    public void setWorkerEntrypoint(String value) {
        workerEntrypoint = value;
    }

    // @NonNull
    // @Override
    // public ListenableFuture<Result> startWork() {
    //     return CallbackToFutureAdapter.getFuture(completer -> {
    //         workCompleter = completer;

    //         pythonThread = new Thread(this);
    //         pythonThread.start();

    //         Log.d("python worker", "PythonWorker thread started");
    //         return "PythonWorker started";
    //     });
    // }

    @Override
    public ListenableFuture<Result> startRemoteWork() {
        return CallbackToFutureAdapter.getFuture(completer -> {
            Log.i("python worker", "Starting ");

            workCompleter = completer;

            pythonThread = new Thread(this);
            pythonThread.start();

            Log.d("python worker", "PythonWorker thread started");
            return "PythonWorker started";
        });
    }

    @Override
    public void run() {
        File appRootFile = new File(appRoot);

        PythonUtil.loadLibraries(
            appRootFile,
            new File(getApplicationContext().getApplicationInfo().nativeLibraryDir)
        );

        int res = nativeStart(
            androidPrivate, androidArgument,
            workerEntrypoint, pythonName,
            pythonHome, pythonPath,
            pythonServiceArgument
        );

        if (res == 0) {
            workCompleter.set(Result.success());
        } else {
            workCompleter.set(Result.failure());
        }
        Log.d("python worker", "PythonWorker thread terminating:" + res);
    }

    // Native part
    // XXX: p4a crashes if nativeStart in worker not syncronized
    // public static synchronized native void nativeStart(
    //     String androidPrivate, String androidArgument,
    //     String workerEntrypoint, String pythonName,
    //     String pythonHome, String pythonPath
    // );

    // Native part
    // synchronized is still needed, startRemoteWork gets called on the same service instance
    // XXX: check out how to start a service for each worker
    public static synchronized native int nativeStart(
        String androidPrivate, String androidArgument,
        String workerEntrypoint, String pythonName,
        String pythonHome, String pythonPath,
        String pythonServiceArgument
    );
}
