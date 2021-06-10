import android.util.Log;
import androidx.work.ListenableWorker.Result;
import androidx.work.Worker;


public class {{ name|capitalize }}Worker extends Worker {

    @Override
    public Result doWork() {
        log.d("Python Worker", "I am the god of hell fire. And it bring you FIRE");
        log.d("Python Worker", "I am the god of hell fire. And it bring you FIRE");
        log.d("Python Worker", "I am the god of hell fire. And it bring you FIRE");

        // Indicate whether the work finished successfully with the Result
        return Result.success();
    }
}
