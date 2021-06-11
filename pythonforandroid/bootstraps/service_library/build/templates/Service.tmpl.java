package {{ args.package }};

import java.io.File;

import android.os.Build;
import android.content.Intent;
import android.content.Context;
import android.content.res.Resources;
import android.util.Log;

import org.kivy.android.PythonService;
import org.kivy.android.PythonUtil;

public class Service{{ name|capitalize }} extends PythonService {

    private static final String TAG = "PythonService";

    public static void prepare(Context ctx) {
        String appRoot = PythonUtil.getAppRoot(ctx);
        Log.v(TAG, "Ready to unpack");
        File app_root_file = new File(appRoot);
        PythonUtil.unpackData(ctx, "private", app_root_file, false);
    }

    public static void start(Context ctx, String pythonServiceArgument) {
        String appRoot = PythonUtil.getAppRoot(ctx);
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        intent.putExtra("androidPrivate", appRoot);
        intent.putExtra("androidArgument", appRoot);
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
        intent.putExtra("serviceTitle", "{{ name|capitalize }}");
        intent.putExtra("serviceDescription", "");
        intent.putExtra("pythonName", "{{ name }}");
        intent.putExtra("serviceStartAsForeground", "{{ foreground|lower }}");
        intent.putExtra("pythonHome", appRoot);
        intent.putExtra("androidUnpack", appRoot);
        intent.putExtra("pythonPath", appRoot + ":" + appRoot + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);

        //foreground: {{foreground}}
        {% if foreground %}
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            ctx.startForegroundService(intent);
        } else {
            ctx.startService(intent);
        }
        {% else %}
        ctx.startService(intent);
        {% endif %}
    }
}
