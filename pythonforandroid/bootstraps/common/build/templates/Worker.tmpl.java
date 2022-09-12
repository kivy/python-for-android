package {{ args.package }};

import android.content.Context;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.work.Data;
import androidx.work.WorkRequest;
import androidx.work.WorkerParameters;

import org.kivy.android.PythonWorker;

public class {{ name|capitalize }}Worker extends PythonWorker {
    private static final String TAG = "{{ name|capitalize }}Worker";

    public static {{ name|capitalize }}Worker mWorker = null;

    public {{ name|capitalize }}Worker (
        @NonNull Context context,
        @NonNull WorkerParameters params) {
        super(context, params);
        setPythonName("{{ name }}");
        setWorkerEntrypoint("{{ entrypoint }}");
        mWorker = this;
    }

    public static Data buildInputData (String serviceArgument) {
        String dataArgument = serviceArgument == null ? "" : serviceArgument;
        Data data = new Data.Builder()
            .putString(ARGUMENT_SERVICE_ARGUMENT, dataArgument)
            .putString(ARGUMENT_PACKAGE_NAME, "{{ args.package }}")
            .putString(ARGUMENT_CLASS_NAME,
                       {{ name|capitalize }}WorkerService.class.getName())
            .build();
        Log.v(TAG, "Request data: " + data.toString());
        return data;
    }

    public static WorkRequest buildWorkRequest (
        WorkRequest.Builder builder,
        String serviceArgument) {
        Data data = buildInputData(serviceArgument);
        return builder.setInputData(data).build();
    }
}
