package {{ args.package }};

import android.content.Intent;
import android.content.Context;
import {{ args.service_class_name }};
import org.kivy.android.PythonServiceIntent;


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

    static private void _start(Context ctx, String smallIconName,
                               String contentTitle, String contentText,
                               String pythonServiceArgument) {
        Intent intent = getDefaultIntent(ctx, smallIconName, contentTitle,
            contentText, pythonServiceArgument);
        ctx.startService(intent);
    }

    static public void start(Context ctx, String pythonServiceArgument) {
        _start(ctx, "", "{{ args.name }}", "{{ name|capitalize }}", pythonServiceArgument);
    }

    static public void start(Context ctx, String smallIconName,
                             String contentTitle, String contentText,
                             String pythonServiceArgument) {
        _start(ctx, smallIconName, contentTitle, contentText, pythonServiceArgument);
    }

    static public Intent getDefaultIntent(Context ctx, String smallIconName,
                                          String contentTitle, String contentText,
                                          String pythonServiceArgument) {
        return PythonServiceIntent.build(
            ctx,
            Service{{ name|capitalize }}.class,
            "{{ entrypoint }}",
            "{{ args.name }}",
            "{{ name }}",
            "{{ foreground|lower }}",
            pythonServiceArgument,
            smallIconName,
            contentTitle,
            contentText);
    }

    @Override
    protected Intent getThisDefaultIntent(Context ctx, String pythonServiceArgument) {
        return Service{{ name|capitalize }}.getDefaultIntent(ctx, "", "", "",
            pythonServiceArgument);
    }

    static public void stop(Context ctx) {
        PythonServiceIntent.stop(ctx, Service{{ name|capitalize }}.class);
    }
}
