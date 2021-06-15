package {{ args.package }};

import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;

import org.kivy.android.PythonBoundService;

public class Service{{ name|capitalize }} extends PythonBoundService {
    // Binder given to clients
    private final IBinder binder = new {{ name|capitalize }}Binder();

    // Class used for the client Binder. Because we know this service always
    // runs in the same process as its clients, we don't need to deal with IPC.
    public class {{ name|capitalize }}Binder extends Binder {
        public Service{{ name|capitalize }} getService() {
            // Return this instance of LocalService so clients can call public methods
            return Service{{ name|capitalize }}.this;
        }
    }

    public Service{{ name|capitalize }}() {
        super();
        setPythonName("{{ name }}");
        setWorkerEntrypoint("{{ entrypoint }}");
    }

    @Override
    public IBinder onBind(Intent intent) {
        startPythonThread();
        return binder;
    }
}
