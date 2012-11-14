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
import android.net.ConnectivityManager;
import android.net.NetworkInfo;

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
     public static void vibrate(double s) {
         Vibrator v = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);
         if (v != null) {
             v.vibrate((int) (1000 * s));
         }
     }

     public static SensorEvent lastEvent = null;

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
     public static void accelerometerEnable(boolean enable) {
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


     public static float[] accelerometerReading() {
         if (lastEvent != null) {
             return lastEvent.values;
         } else {
             float rv[] = { 0f, 0f, 0f };
             return rv;
         }
     }

     static SensorEvent lastOrientationEvent = null;

     static class OrientationListener implements SensorEventListener {
         public void onSensorChanged(SensorEvent ev) {
             lastOrientationEvent = ev;
         }

         public void onAccuracyChanged(Sensor sensor , int accuracy) {
         }
     }

     static OrientationListener orientationListener = new OrientationListener();

     /**
      * Enable or Disable the OrientationSensor.
      */
     public static void orientationSensorEnable(boolean enable) {
         SensorManager sm = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
         Sensor orientationSensor = sm.getDefaultSensor(Sensor.TYPE_ORIENTATION);

         if (orientationSensor == null) {
             return;
         }

         if (enable) {
             sm.registerListener(orientationListener, orientationSensor, SensorManager.SENSOR_DELAY_NORMAL);
         } else {
             sm.unregisterListener(orientationListener, orientationSensor);
         }
     }

     public static float[] orientationSensorReading() {
         if (lastOrientationEvent != null) {
             return lastOrientationEvent.values;
         } else {
             float rv[] = { 0f, 0f, 0f };
             return rv;
         }
     }

     static SensorEvent lastMagneticFieldEvent = null;

     static class MagneticFieldListener implements SensorEventListener {
         public void onSensorChanged(SensorEvent ev) {
             lastMagneticFieldEvent = ev;
         }

         public void onAccuracyChanged(Sensor sensor , int accuracy) {
         }
     }

     static MagneticFieldListener magneticFieldListener = new MagneticFieldListener();

     /**
      * Enable or Disable the MagneticFieldSensor.
      */
     public static void magneticFieldSensorEnable(boolean enable) {
         SensorManager sm = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
         Sensor magneticFieldSensor = sm.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);

         if (magneticFieldSensor == null) {
             return;
         }

         if (enable) {
             sm.registerListener(magneticFieldListener, magneticFieldSensor, SensorManager.SENSOR_DELAY_NORMAL);
         } else {
             sm.unregisterListener(magneticFieldListener, magneticFieldSensor);
         }
     }


     public static float[] magneticFieldSensorReading() {
         if (lastMagneticFieldEvent != null) {
             return lastMagneticFieldEvent.values;
         } else {
             float rv[] = { 0f, 0f, 0f };
             return rv;
         }
     }


     static DisplayMetrics metrics = new DisplayMetrics();

     /**
      * Get display DPI.
      */
     public static int getDPI() {
         return metrics.densityDpi;
     }

     /**
      * Show the soft keyboard.
      */
     public static void showKeyboard() {
         InputMethodManager imm = (InputMethodManager) context.getSystemService(Context.INPUT_METHOD_SERVICE);
         imm.showSoftInput(view, InputMethodManager.SHOW_FORCED);
     }

     /**
      * Hide the soft keyboard.
      */
     public static void hideKeyboard() {
         InputMethodManager imm = (InputMethodManager) context.getSystemService(Context.INPUT_METHOD_SERVICE);
         imm.hideSoftInputFromWindow(view.getWindowToken(), 0);
     }

    /**
     * Scan WiFi networks
     */
    static List<ScanResult> latestResult;

    public static void enableWifiScanner()
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

    public static String scanWifi() {

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

    /**
     * network state
     */

    public static boolean network_state = false;

    /**
    * Check network state directly
    *
	* (only one connection can be active at a given moment, detects all network type)
    *
    */
    public static boolean checkNetwork()
    {
        boolean state = false;
        final ConnectivityManager conMgr =  (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);

		final NetworkInfo activeNetwork = conMgr.getActiveNetworkInfo();
		if (activeNetwork != null && activeNetwork.isConnected()) {
			network_state = true;
		} else {
			network_state = false;
		}

        return state;
    }

    /**
    * To recieve network state changes
    */
    public static void registerNetworkCheck()
    {
        IntentFilter i = new IntentFilter();
        i.addAction(ConnectivityManager.CONNECTIVITY_ACTION);
        context.registerReceiver(new BroadcastReceiver() {

            @Override
            public void onReceive(Context c, Intent i) {
				checkNetwork();
            }

        }, i);
    }

}
