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
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        String argument = ctx.getFilesDir().getAbsolutePath() + "/app";
        intent.putExtra("androidPrivate", ctx.getFilesDir().getAbsolutePath());
        intent.putExtra("androidArgument", argument);
        intent.putExtra("serviceTitle", "{{ args.name }}");
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
        intent.putExtra("pythonName", "{{ name }}");
        intent.putExtra("serviceStartAsForeground", "{{ foreground|lower }}");
        intent.putExtra("pythonHome", argument);
        intent.putExtra("pythonPath", argument + ":" + argument + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);
        intent.putExtra("smallIconName", smallIconName);
        intent.putExtra("contentTitle", contentTitle);
        intent.putExtra("contentText", contentText);
        return intent;
    }

    @Override
    protected Intent getThisDefaultIntent(Context ctx, String pythonServiceArgument) {
        return Service{{ name|capitalize }}.getDefaultIntent(ctx, "", "", "", 
							     pythonServiceArgument);
    }

    static public void stop(Context ctx) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        ctx.stopService(intent);
    }
}
