package org.alanjds.sl4acompat;

import com.googlecode.android_scripting.Log;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;


// Usage: ./adb shell am broadcast -a org.alanjds.sl4acompat.START_MINIMAL_SERVICE

public class MinimalServiceStarter extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        Log.v("Received intent!");
        Intent serviceIntent = new Intent(context, MinimalService.class);
        context.startService(serviceIntent);
        Log.v("Service started?");
    }
} 