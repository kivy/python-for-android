package {{ args.package }};

import android.os.Binder;
import android.os.IBinder;
import android.content.Intent;
import android.content.Context;
import org.kivy.android.PythonService;

public class Service{{ name|capitalize }} extends PythonService {
	/**
	 * Binder given to clients
	 */
    private final IBinder mBinder = new Service{{ name|capitalize }}Binder();

    {% if sticky %}
    /**
     * {@inheritDoc}
     */
    @Override
    public int startType() {
        return START_STICKY;
    }
    {% endif %}

    @Override
    protected int getServiceId() {
        return {{ service_id }};
    }

    public static void start(Context ctx, String pythonServiceArgument) {
        String argument = ctx.getFilesDir().getAbsolutePath() + "/app";
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        intent.putExtra("androidPrivate", argument);
        intent.putExtra("androidArgument", argument);
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
        intent.putExtra("serviceTitle", "{{ name|capitalize }}");
        intent.putExtra("pythonName", "{{ name }}");
        intent.putExtra("serviceStartAsForeground", "{{ foreground|lower }}");
        intent.putExtra("pythonHome", argument);
        intent.putExtra("androidUnpack", argument);
        intent.putExtra("pythonPath", argument + ":" + argument + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);
        intent.putExtra("smallIconName", "");
        intent.putExtra("contentTitle", "{{ name|capitalize }}");
        intent.putExtra("contentText", "");	    
        ctx.startService(intent);
    }
	
    public static void start(Context ctx, String smallIconName,
			     String contentTitle,
			     String contentText,
			     String pythonServiceArgument) {	
        String argument = ctx.getFilesDir().getAbsolutePath() + "/app";
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        intent.putExtra("androidPrivate", argument);
        intent.putExtra("androidArgument", argument);
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
        intent.putExtra("serviceTitle", "{{ name|capitalize }}");
        intent.putExtra("pythonName", "{{ name }}");
        intent.putExtra("serviceStartAsForeground", "{{ foreground|lower }}");
        intent.putExtra("pythonHome", argument);
        intent.putExtra("androidUnpack", argument);
        intent.putExtra("pythonPath", argument + ":" + argument + "/lib");
        intent.putExtra("pythonServiceArgument", pythonServiceArgument);
        intent.putExtra("smallIconName", smallIconName);
        intent.putExtra("contentTitle", contentTitle);
        intent.putExtra("contentText", contentText);	    
        ctx.startService(intent);
    }
	
    public static void stop(Context ctx) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        ctx.stopService(intent);
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    /**
     * Class used for the client Binder. Because we know this service always
     * runs in the same process as its clients, we don't need to deal with IPC.
     */
    public class Service{{ name|capitalize }}Binder extends Binder {
    	Service{{ name|capitalize }} getService() {
            // Return this instance of Service{{ name|capitalize }} so clients can call public methods
            return Service{{ name|capitalize }}.this;
        }
    }
}
