package org.kivy.android;

import android.util.Log;

import java.io.IOException;
import java.net.Socket;
import java.net.InetSocketAddress;

import android.os.SystemClock;

import android.os.Handler;

import org.kivy.android.PythonActivity;

public class WebViewLoader {
    private static final String TAG = "WebViewLoader";

    public static void testConnection() {

        while (true) {
            if (WebViewLoader.pingHost("localhost", {{ args.port }}, 100)) {
                Log.v(TAG, "Successfully pinged localhost:{{ args.port }}");
                Handler mainHandler = new Handler(PythonActivity.mActivity.getMainLooper());
                Runnable myRunnable = new Runnable() {
                        @Override
                        public void run() {
                            PythonActivity.mActivity.loadUrl("http://127.0.0.1:{{ args.port }}/");
                            Log.v(TAG, "Loaded webserver in webview");
                        }
                    };
                mainHandler.post(myRunnable);
                break;

            } else {
                Log.v(TAG, "Could not ping localhost:{{ args.port }}");
                try {
                    Thread.sleep(100);
                } catch(InterruptedException e) {
                    Log.v(TAG, "InterruptedException occurred when sleeping");
                }
            }
        }
    }

    public static boolean pingHost(String host, int port, int timeout) {
        Socket socket = new Socket();
        try {
            socket.connect(new InetSocketAddress(host, port), timeout);
            socket.close();
            return true;
        } catch (IOException e) {
            try {socket.close();} catch (IOException f) {return false;}
            return false; // Either timeout or unreachable or failed DNS lookup.
        }
    }
}
