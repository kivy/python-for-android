package {{ args.package }};

import java.io.File;

import android.os.Build;
import android.content.Intent;
import android.content.Context;
import android.content.res.Resources;
import android.util.Log;

import org.kivy.android.PythonService;
import org.kivy.android.PythonServiceIntent;
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
	
    static private void _start(Context ctx, String smallIconName,
			     String contentTitle,
			     String contentText,
			     String pythonServiceArgument) {
        Intent intent = getDefaultIntent(ctx, smallIconName, contentTitle,
                                         contentText, pythonServiceArgument);
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

    public static void start(Context ctx, String pythonServiceArgument) {
	_start(ctx,  "", "{{ args.name }}", "{{ name|capitalize }}", pythonServiceArgument);
    }
    
    static public void start(Context ctx, String smallIconName,
			     String contentTitle,
			     String contentText,
			     String pythonServiceArgument) {
	_start(ctx, smallIconName, contentTitle, contentText, pythonServiceArgument);
    }

    static public Intent getDefaultIntent(Context ctx, String smallIconName,
					  String contentTitle,
					  String contentText,
					  String pythonServiceArgument) {
        String appRoot = PythonUtil.getAppRoot(ctx);
        return PythonServiceIntent.buildWithPaths(
            ctx,
            Service{{ name|capitalize }}.class,
            appRoot,
            appRoot,
            appRoot,
            "{{ entrypoint }}",
            "{{ name|capitalize }}",
            null,
            "{{ name }}",
            "{{ foreground|lower }}",
            pythonServiceArgument,
            smallIconName,
            contentTitle,
            contentText);
    }

    @Override
    protected Intent getThisDefaultIntent(Context ctx, String pythonServiceArgument) {
        return Service{{ name|capitalize }}.getDefaultIntent(ctx,  "", "", "",
                                                             pythonServiceArgument);
    }



    static public void stop(Context ctx) {
        PythonServiceIntent.stop(ctx, Service{{ name|capitalize }}.class);
    }

}
