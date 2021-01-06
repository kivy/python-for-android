package {{ args.package }};

import android.content.Intent;
import android.content.Context;
import org.kivy.android.PythonService;
import java.io.File;


public class Service{{ name|capitalize }} extends PythonService {
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

    static public void start(Context ctx, String pythonServiceArgument) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        String argument = ctx.getFilesDir().getAbsolutePath() + "/app";
        intent.putExtra("androidPrivate", ctx.getFilesDir().getAbsolutePath());
        intent.putExtra("androidArgument", argument);
        intent.putExtra("serviceTitle", "{{ args.name }}");
        intent.putExtra("serviceDescription", "{{ name|capitalize }}");
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
        intent.putExtra("pythonName", "{{ name }}");
        intent.putExtra("serviceStartAsForeground", "{{ foreground|lower }}");
        intent.putExtra("pythonHome", argument);
        intent.putExtra("pythonPath", argument + ":" + argument + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);
        ctx.startService(intent);
    }

    @Override
    public void run(){
        String package_root = getFilesDir().getAbsolutePath();
        String app_root =  package_root + "/app";
        File app_root_file = new File(app_root);
        if (androidPrivate == null) {
            androidPrivate = package_root;
        }
        if (androidArgument == null) {
            androidArgument = app_root;
        }
        if (serviceEntrypoint == null) {
            serviceEntrypoint ="{{ entrypoint }}";
        }
        if (pythonName == null) {
            pythonName = "{{ name }}";
        }
        if (pythonHome == null) {
            pythonHome = app_root;
        }
        if (pythonPath == null) {
            pythonPath = package_root;
        }
        if (pythonServiceArgument == null) {
            pythonServiceArgument = app_root+":"+app_root+"/lib";
        }
        super.run();
    }

    static public void stop(Context ctx) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        ctx.stopService(intent);
    }
}
