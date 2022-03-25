package {{ args.package }};

import android.content.Context;
import androidx.annotation.NonNull;
import androidx.work.WorkerParameters;
import org.kivy.android.PythonWorker;


public class {{ name|capitalize }}Worker extends PythonWorker {
    public static {{ name|capitalize }}Worker mWorker = null;

    public {{ name|capitalize }}Worker (
        @NonNull Context context,
        @NonNull WorkerParameters params) {
        super(context, params);
        setPythonName("{{ name }}");
        setWorkerEntrypoint("{{ entrypoint }}");
        mWorker = this;
    }
}
