package {{ args.package }};

import android.content.Context;
import androidx.annotation.NonNull;
import androidx.work.WorkerParameters;
import org.kivy.android.PythonWorker;
import org.kivy.android.PythonActivity;


public class {{ name|capitalize }}Worker extends PythonWorker {

    public {{ name|capitalize }}Worker (
        @NonNull Context context,
        @NonNull WorkerParameters params) {
        super(context, params);
        setPythonName("{{ name }}");
        setWorkerEntrypoint("{{ entrypoint }}");
    }
}
