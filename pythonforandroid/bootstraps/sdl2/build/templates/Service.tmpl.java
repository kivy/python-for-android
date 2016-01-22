package {{ args.package }};

import android.content.Intent;
import android.content.Context;
import org.kivy.android.PythonService;
import org.kivy.android.PythonActivity;


public class Service{{ name|capitalize }} extends PythonService {
    @Override
    public boolean canDisplayNotification() {
        return false;
    }

    static public void start(Context ctx, String pythonServiceArgument) {
        Intent intent = new Intent(ctx, Service{{ name|capitalize }}.class);
        String argument = ctx.getFilesDir().getAbsolutePath();
        intent.putExtra("androidPrivate", argument);
        intent.putExtra("androidArgument", argument);
        intent.putExtra("serviceEntrypoint", "{{ entrypoint }}");
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
