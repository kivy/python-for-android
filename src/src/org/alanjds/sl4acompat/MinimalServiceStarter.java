package org.alanjds.sl4acompat;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class MinimalServiceStarter extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        Intent service = new Intent(context, MinimalService.class);
        context.startService(service);
    }
} 