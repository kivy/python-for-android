package {{ args.package }};

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;

import android.os.Build;
import android.content.Intent;
import android.content.Context;
import android.content.res.Resources;
import android.util.Log;

import org.renpy.android.AssetExtract;
import org.kivy.android.PythonService;

public class Service{{ name|capitalize }} extends PythonService {

    private static final String TAG = "PythonService";

    public static void prepare(Context ctx) {
        String appRoot = getAppRoot(ctx);
        Log.v(TAG, "Ready to unpack");
        File app_root_file = new File(appRoot);
        unpackData(ctx, "private", app_root_file);
    }

    public static void start(Context ctx, String pythonServiceArgument) {
        String appRoot = getAppRoot(ctx);
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

    public static String getAppRoot(Context ctx) {
        String app_root = ctx.getFilesDir().getAbsolutePath() + "/app";
        return app_root;
    }

    public static String getResourceString(Context ctx, String name) {
        // Taken from org.renpy.android.ResourceManager
        Resources res = ctx.getResources();
        int id = res.getIdentifier(name, "string", ctx.getPackageName());
        return res.getString(id);
    }

    public static void unpackData(Context ctx, final String resource, File target) {
        // Taken from PythonActivity class

        Log.v(TAG, "UNPACKING!!! " + resource + " " + target.getName());

        // The version of data in memory and on disk.
        String data_version = getResourceString(ctx, resource + "_version");
        String disk_version = null;

        Log.v(TAG, "Data version is " + data_version);

        // If no version, no unpacking is necessary.
        if (data_version == null) {
            return;
        }

        // Check the current disk version, if any.
        String filesDir = target.getAbsolutePath();
        String disk_version_fn = filesDir + "/" + resource + ".version";

        try {
            byte buf[] = new byte[64];
            InputStream is = new FileInputStream(disk_version_fn);
            int len = is.read(buf);
            disk_version = new String(buf, 0, len);
            is.close();
        } catch (Exception e) {
            disk_version = "";
        }

        // If the disk data is out of date, extract it and write the
        // version file.
        // if (! data_version.equals(disk_version)) {
        if (! data_version.equals(disk_version)) {
            Log.v(TAG, "Extracting " + resource + " assets.");

            // Don't delete existing files
            // recursiveDelete(target);
            target.mkdirs();

            AssetExtract ae = new AssetExtract(ctx);
            if (!ae.extractTar(resource + ".mp3", target.getAbsolutePath())) {
                Log.v(TAG, "Could not extract " + resource + " data.");
            }

            try {
                // Write .nomedia.
                new File(target, ".nomedia").createNewFile();

                // Write version file.
                FileOutputStream os = new FileOutputStream(disk_version_fn);
                os.write(data_version.getBytes());
                os.close();
            } catch (Exception e) {
                Log.w("python", e);
            }
        }
    }

}
