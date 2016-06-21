package {{ args.package }};

import android.content.Intent;
import android.content.Context;
import org.kivy.android.PythonService;


public class Service{{ name|capitalize }} extends PythonService {
    {% if sticky %}
    /**
     * {@inheritDoc}
     */
    @Override
    public int startType() {
        return START_STICKY;
    }
    {% endif %}

    {% if not foreground %}
    /**
     * {@inheritDoc}
     */
    @Override
    public boolean canDisplayNotification() {
        return false;
    }
    {% endif %}

    public static void start(Context ctx, String pythonServiceArgument) {
    	String argument = ctx.getFilesDir().getAbsolutePath();
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        intent.putExtra("androidPrivate", argument);
        intent.putExtra("androidArgument", argument);
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
        intent.putExtra("serviceTitle", "{{ name|capitalize }}");
        intent.putExtra("serviceDescription", "");
        intent.putExtra("pythonName", "{{ name }}");
        intent.putExtra("pythonHome", argument);
        intent.putExtra("pythonPath", argument + ":" + argument + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);
        ctx.startService(intent);
    }
    
    public static void stop(Context ctx) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        ctx.stopService(intent);
    }

}
