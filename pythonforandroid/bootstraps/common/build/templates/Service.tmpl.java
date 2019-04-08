package {{ args.package }};

import android.os.Build;
import java.lang.reflect.Method;
import java.lang.reflect.InvocationTargetException;
import android.content.Intent;
import android.content.Context;
import android.app.Notification;
import android.app.PendingIntent;
import android.os.Bundle;
import org.kivy.android.PythonService;
import org.kivy.android.PythonActivity;

import android.content.pm.PackageManager;
import android.support.v4.app.ActivityCompat;
import android.Manifest;
import android.app.NotificationChannel;
import android.app.Notification;
import android.app.NotificationManager;
import android.content.Context;
import android.support.v4.app.NotificationCompat;
import android.graphics.Color;
import android.app.Service;
import android.content.ComponentName;
import android.app.PendingIntent;

public class Service{{ name|capitalize }} extends PythonService {

    private boolean autoRestartService = true;

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
        Notification notification;
        Context context = getApplicationContext();
        Intent contextIntent = new Intent(context, PythonActivity.class);
        PendingIntent pIntent = PendingIntent.getActivity(context, 0, contextIntent,
            PendingIntent.FLAG_UPDATE_CURRENT);
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.HONEYCOMB) {
            notification = new Notification(
                context.getApplicationInfo().icon, "{{ args.name }}", System.currentTimeMillis());
            try {
                // prevent using NotificationCompat, this saves 100kb on apk
                Method func = notification.getClass().getMethod(
                    "setLatestEventInfo", Context.class, CharSequence.class,
                    CharSequence.class, PendingIntent.class);
                func.invoke(notification, context, "{{ args.name }}", "{{ name| capitalize }}", pIntent);
            } catch (NoSuchMethodException | IllegalAccessException |
                     IllegalArgumentException | InvocationTargetException e) {
            }
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            String channelName = "{{ name| capitalize }}";
            NotificationChannel chan = new NotificationChannel("{{ args.name }}", channelName, NotificationManager.IMPORTANCE_MIN);
            chan.setLightColor(Color.BLUE);
            chan.setLockscreenVisibility(Notification.VISIBILITY_PRIVATE);

            NotificationManager manager = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
            assert manager != null;
            manager.createNotificationChannel(chan);

            NotificationCompat.Builder notificationBuilder = new NotificationCompat.Builder(context, "{{ args.name }}");
            notification = notificationBuilder.setOngoing(true)
                    .setSmallIcon(context.getApplicationInfo().icon)
                    .setContentTitle(channelName)
                    .setContentIntent(pIntent)
                    .setPriority(Notification.PRIORITY_MIN)
                    .setShowWhen(false)
                    .setOnlyAlertOnce(true)             
                    .build();
        } else {
            Notification.Builder builder = new Notification.Builder(context);
            builder.setContentTitle("{{ args.name }}");
            builder.setContentText("{{ name| capitalize }}");
            builder.setContentIntent(pIntent);
            builder.setSmallIcon(context.getApplicationInfo().icon);
            notification = builder.build();
        }        
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
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            ctx.startForegroundService(intent);
        } else {
            ctx.startService(intent);
        }
    }


    @Override
    public void onDestroy() {
        super.onDestroy();
    }


    static public void stop(Context ctx) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        ctx.stopService(intent);
    }
}
