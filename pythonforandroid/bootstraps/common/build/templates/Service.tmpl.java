package {{ args.package }};

import android.content.Intent;
import android.content.Context;
import {{ args.service_class_name }};


public class Service{{ name|capitalize }} extends {{ base_service_class }} {
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
        Intent intent = getDefaultIntent(ctx, pythonServiceArgument);
        ctx.startService(intent);
    }

    static public Intent getDefaultIntent(Context ctx, String pythonServiceArgument) {
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
