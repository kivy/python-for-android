package org.renpy.android;

import android.content.Context;
import android.os.Vibrator;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.util.DisplayMetrics;
import android.view.inputmethod.InputMethodManager;
import android.view.View;

import java.util.List;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.IntentFilter;

/**
 * Methods that are expected to be called via JNI, to access the
 * device's non-screen hardware. (For example, the vibration and
 * accelerometer.)
 */
public class Hardware {

     // The context.
     static Context context;
     static View view;

     /**
      * Vibrate for s seconds.
      */
     static void vibrate(double s) {
         Vibrator v = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
         if (v != null) {
             v.vibrate((int) (1000 * s));
         }
     }

     static SensorEvent lastEvent = null;

     static class AccelListener implements SensorEventListener {
         public void onSensorChanged(SensorEvent ev) {
             lastEvent = ev;
         }

         public void onAccuracyChanged(Sensor sensor , int accuracy) {
         }

     }

     static AccelListener accelListener = new AccelListener();

     /**
      * Enable or Disable the accelerometer.
      */
     static void accelerometerEnable(boolean enable) {
         SensorManager sm = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
         Sensor accel = sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

         if (accel == null) {
             return;
         }

         if (enable) {
             sm.registerListener(accelListener, accel, SensorManager.SENSOR_DELAY_GAME);
         } else {
             sm.unregisterListener(accelListener, accel);

         }
     }


     static float[] accelerometerReading() {
         if (lastEvent != null) {
             return lastEvent.values;
         } else {
             float rv[] = { 0f, 0f, 0f };
             return rv;
         }
     }

     static DisplayMetrics metrics = new DisplayMetrics();

     /**
      * Get display DPI.
      */
     static int getDPI() {
         return metrics.densityDpi;
     }

     /**
      * Show the soft keyboard.
      */
     static void showKeyboard() {
         InputMethodManager imm = (InputMethodManager) context.getSystemService(Context.INPUT_METHOD_SERVICE);
         imm.showSoftInput(view, InputMethodManager.SHOW_FORCED);
     }

     /**
      * Hide the soft keyboard.
      */
     static void hideKeyboard() {
         InputMethodManager imm = (InputMethodManager) context.getSystemService(Context.INPUT_METHOD_SERVICE);
         imm.hideSoftInputFromWindow(view.getWindowToken(), 0);
     }

    /**
     * Scan WiFi networks
     */
    static List<ScanResult> latestResult;

    static void enableWifiScanner()
    {
        IntentFilter i = new IntentFilter();
        i.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);

        context.registerReceiver(new BroadcastReceiver() {

            @Override
            public void onReceive(Context c, Intent i) {
                // Code to execute when SCAN_RESULTS_AVAILABLE_ACTION event occurs
                WifiManager w = (WifiManager) c.getSystemService(Context.WIFI_SERVICE);
                latestResult = w.getScanResults(); // Returns a <list> of scanResults
            }

        }, i);

    }

    static String scanWifi() {

        // Now you can call this and it should execute the broadcastReceiver's
        // onReceive()
        WifiManager wm = (WifiManager) context.getSystemService(Context.WIFI_SERVICE);
        boolean a = wm.startScan();

        if (latestResult != null){

            String latestResultString = "";
            for (ScanResult result : latestResult)
            {
                latestResultString += String.format("%s\t%s\t%d\n", result.SSID, result.BSSID, result.level);
            }

            return latestResultString;
        }

        return "";
    }

}
