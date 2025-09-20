package org.kivy.android;

import android.content.Intent;
import android.content.Context;

public interface GenericBroadcastReceiverCallback {
    void onReceive(Context context, Intent intent);
};
