package {{ args.package }};

import android.os.Binder;
import android.os.IBinder;
import android.content.Intent;
import android.content.Context;
import org.kivy.android.PythonService;
import org.kivy.android.PythonServiceIntent;
import org.kivy.android.PythonUtil;

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
        Intent intent = getDefaultIntent(ctx, "", "{{ name|capitalize }}", "",
            pythonServiceArgument);
        ctx.startService(intent);
    }
	
    public static void start(Context ctx, String smallIconName,
			     String contentTitle,
			     String contentText,
			     String pythonServiceArgument) {	
        Intent intent = getDefaultIntent(ctx, smallIconName, contentTitle,
            contentText, pythonServiceArgument);
        ctx.startService(intent);
    }

    public static Intent getDefaultIntent(Context ctx, String smallIconName,
                                          String contentTitle, String contentText,
                                          String pythonServiceArgument) {
        String appRoot = PythonUtil.getAppRoot(ctx);
        return PythonServiceIntent.buildWithPaths(
            ctx,
            Service{{ name|capitalize }}.class,
            appRoot,
            appRoot,
            appRoot,
            "{{ entrypoint }}",
            "{{ name|capitalize }}",
            null,
            "{{ name }}",
            "{{ foreground|lower }}",
            pythonServiceArgument,
            smallIconName,
            contentTitle,
            contentText);
    }
	
    public static void stop(Context ctx) {
        PythonServiceIntent.stop(ctx, Service{{ name|capitalize }}.class);
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
