package org.alanjds.sl4acompat;

import com.googlecode.android_scripting.Log;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;


public class MinimalServiceStarter extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.v("Received intent!");
        Intent serviceIntent = new Intent(context, MinimalService.class);
        context.startService(serviceIntent);
        Log.v("Service started?");
    }
} 