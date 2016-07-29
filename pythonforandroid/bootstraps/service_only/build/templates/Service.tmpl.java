package {{ args.package }};

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
    public int getStartType() {
        return START_STICKY;
    }
    {% endif %}

    {% if foreground %}
    /**
     * {@inheritDoc}
     */
    @Override
    public boolean getStartForeground() {
        return true;
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

    /**
     * {@inheritDoc}
     */
    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }
}
