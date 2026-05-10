package org.kivy.android;

import android.content.Context;
import android.content.Intent;

public interface GenericBroadcastReceiverCallback {
    void onReceive(Context context, Intent intent);
}
;
