package {{ args.package }};

import android.content.Intent;
import android.content.Context;
import android.app.Notification;
import android.app.PendingIntent;
import android.os.Bundle;
import org.kivy.android.PythonService;
import org.kivy.android.PythonActivity;


public class Service{{ name|capitalize }} extends PythonService {
    {% if sticky %}
    @Override
    public int startType() {
        return START_STICKY;
    }
    {% endif %}

    {% if not foreground %}
    @Override
    public boolean canDisplayNotification() {
        return false;
    }
    {% endif %}

    @Override
    protected void doStartForeground(Bundle extras) {
        Context context = getApplicationContext();
        Notification notification = new Notification(context.getApplicationInfo().icon,
            "{{ args.name }}", System.currentTimeMillis());
        Intent contextIntent = new Intent(context, PythonActivity.class);
        PendingIntent pIntent = PendingIntent.getActivity(context, 0, contextIntent,
            PendingIntent.FLAG_UPDATE_CURRENT);
        notification.setLatestEventInfo(context, "{{ args.name }}", "{{ name| capitalize }}", pIntent);
        startForeground({{ service_id }}, notification);
    }

    static public void start(Context ctx, String pythonServiceArgument) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        String argument = ctx.getFilesDir().getAbsolutePath() + "/app";
        intent.putExtra("androidPrivate", ctx.getFilesDir().getAbsolutePath());
        intent.putExtra("androidArgument", argument);
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
        intent.putExtra("pythonName", "{{ name }}");
        intent.putExtra("pythonHome", argument);
        intent.putExtra("pythonPath", argument + ":" + argument + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);
        ctx.startService(intent);
    }

    static public void stop(Context ctx) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        ctx.stopService(intent);
    }
}
