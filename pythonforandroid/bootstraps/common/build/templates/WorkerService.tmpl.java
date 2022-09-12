package {{ args.package }};

import android.content.Context;
import android.util.Log;

import androidx.work.Configuration;
import androidx.work.multiprocess.RemoteWorkerService;
import androidx.work.WorkManager;

import java.lang.System;

public class {{ name|capitalize }}WorkerService extends RemoteWorkerService {
    private static final String TAG = "{{ name|capitalize }}WorkerService";

    @Override
    public void onCreate() {
        try {
            Log.v(TAG, "Initializing WorkManager");
            Context context = getApplicationContext();
            Configuration configuration = new Configuration.Builder()
                .setDefaultProcessName(context.getPackageName())
                .build();
            WorkManager.initialize(context, configuration);
        } catch (IllegalStateException e) {
        }
        super.onCreate();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();

        // The process needs to exit when the service is destroyed since
        // p4a doesn't support starting a Python interpreter more than
        // once per process. Combined with the stopWithTask="true"
        // configuration in the manifest, this should ensure that the
        // service process exits when a task completes.
        Log.v(TAG, "Exiting service process");
        System.exit(0);
    }
}
