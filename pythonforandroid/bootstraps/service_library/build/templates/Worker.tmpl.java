package {{ args.package }};

import android.content.Context;
import android.util.Log;
import androidx.annotation.NonNull;
import androidx.work.ListenableWorker.Result;
import androidx.work.Worker;
import androidx.work.WorkerParameters;


public class {{ name|capitalize }}Worker extends Worker {

    public {{ name|capitalize }}Worker (
        @NonNull Context context,
        @NonNull WorkerParameters params) {
        super(context, params);
    }

    @Override
    public Result doWork() {
        Log.d("Python Worker", "I am the god of hell fire. And it bring you FIRE");

        // Indicate whether the work finished successfully with the Result
        return Result.success();
    }
}
