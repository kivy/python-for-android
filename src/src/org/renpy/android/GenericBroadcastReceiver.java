package org.renpy.android;

import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.Context;

public class GenericBroadcastReceiver extends BroadcastReceiver {

    GenericBroadcastReceiverCallback listener;

    public GenericBroadcastReceiver(GenericBroadcastReceiverCallback listener) {
        super();
        this.listener = listener;
    }

    public void onReceive(Context context, Intent intent) {
        this.listener.onReceive(context, intent);
    }
}
