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
            if (WebViewLoader.pingHost("localhost", 5000, 100)) {
                Log.v(TAG, "successfully pinged localhost");
                // PythonActivity.mWebView.loadUrl("http://localhost:5000");
                // PythonActivity.mWebView.loadUrl("http://www.google.com");
                
                Handler mainHandler = new Handler(PythonActivity.mActivity.getMainLooper());
                
                Runnable myRunnable = new Runnable() {
                        @Override
                        public void run() {
                            // PythonActivity.mActivity.mWebView.loadUrl("http://127.0.0.1:5000/");
                            // PythonActivity.mActivity.mWebView.loadUrl("http://www.google.com");
                            PythonActivity.mActivity.mWebView.loadUrl("file:///" + PythonActivity.mActivity.getFilesDir().getAbsolutePath() + "/load_immediate.html");
                            // PythonActivity.mActivity.mWebView.loadUrl("file:///" + PythonActivity.mActivity.getFilesDir().getAbsolutePath() + "/_load2.html");
                            Log.v(TAG, "did webview load!");
                        }
                        // public void run() {PythonActivity.mActivity.mWebView.loadUrl("http://127.0.0.1:5000");}
                    };
                mainHandler.post(myRunnable);
                break;
                    
            } else {
                Log.v(TAG, "could not ping localhost");
                try {
                    Thread.sleep(100);
                } catch(InterruptedException e) {
                    Log.v(TAG, "InterruptedException occurred when sleeping");
                }
            }
        }
        
        Log.v(TAG, "testConnection finished");
        
    }

    public static boolean pingHost(String host, int port, int timeout) {
        Socket socket = new Socket();
        try {
            socket.connect(new InetSocketAddress(host, port), timeout);
            return true;
        } catch (IOException e) {
            return false; // Either timeout or unreachable or failed DNS lookup.
        }
    }
}
        

