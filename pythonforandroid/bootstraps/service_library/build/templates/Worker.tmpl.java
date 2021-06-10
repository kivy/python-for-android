package {{ args.package }};

import android.content.Context;
import android.util.Log;
import androidx.annotation.NonNull;
import androidx.concurrent.futures.CallbackToFutureAdapter.Completer;
import androidx.concurrent.futures.CallbackToFutureAdapter;
import androidx.work.ListenableWorker.Result;
import androidx.work.ListenableWorker;
import androidx.work.Worker;
import androidx.work.WorkerParameters;
import com.google.common.util.concurrent.ListenableFuture;


public class {{ name|capitalize }}Worker extends ListenableWorker implements Runnable {
    Thread pythonThread = null;
    Completer workCompleter = null;

    public {{ name|capitalize }}Worker (
        @NonNull Context context,
        @NonNull WorkerParameters params) {
        super(context, params);
    }

    @NonNull
    @Override
    public ListenableFuture<Result> startWork() {
        return CallbackToFutureAdapter.getFuture(completer -> {
            workCompleter = completer;

            pythonThread = new Thread(this);
            pythonThread.start();

            String msg = "{{ name|capitalize }}Worker started";
            Log.d("Python Worker", msg);
            return msg;
        });
    }

    @Override
    public void run() {
        Log.d("Python Worker", "I am the god of hell fire. And it bring you FIRE");

        try {
            Thread.sleep(2000);
        } catch (InterruptedException e) {}

        workCompleter.set(Result.success());
        Log.d("Python Worker", "{{ name|capitalize }}Worker Thread terminating");
    }
}
