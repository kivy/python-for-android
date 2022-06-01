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

    {% if sticky %}
    @Override
    public int startType() {
        return START_STICKY;
    }
    {% endif %}

    @Override
    protected int getServiceId() {
        return {{ service_id }};
    }

    public static void prepare(Context ctx) {
        String appRoot = PythonUtil.getAppRoot(ctx);
        Log.v(TAG, "Ready to unpack");
        File app_root_file = new File(appRoot);
        PythonUtil.unpackAsset(ctx, "private", app_root_file, true);
        PythonUtil.unpackPyBundle(ctx, ctx.getApplicationInfo().nativeLibraryDir + "/" + "libpybundle", app_root_file, false);
    }

    public static void start(Context ctx, String pythonServiceArgument) {
        Intent intent = getDefaultIntent(ctx, pythonServiceArgument);

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

    static public Intent getDefaultIntent(Context ctx, String pythonServiceArgument) {
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
        return intent;
    }

    @Override
    protected Intent getThisDefaultIntent(Context ctx, String pythonServiceArgument) {
        return Service{{ name|capitalize }}.getDefaultIntent(ctx, pythonServiceArgument);
    }



    static public void stop(Context ctx) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        ctx.stopService(intent);
    }

}
