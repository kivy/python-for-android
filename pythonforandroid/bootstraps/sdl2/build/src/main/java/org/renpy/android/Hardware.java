package org.renpy.android;

import android.content.Context;
import android.os.Vibrator;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.util.DisplayMetrics;
import android.view.inputmethod.InputMethodManager;
import android.view.inputmethod.EditorInfo;
import android.view.View;

import java.util.List;
import java.util.ArrayList;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.content.BroadcastReceiver;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;

import org.kivy.android.PythonActivity;

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

    /**
     * Get an Overview of all Hardware Sensors of an Android Device
     */
    public static String getHardwareSensors() {
        SensorManager sm = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
        List<Sensor> allSensors = sm.getSensorList(Sensor.TYPE_ALL);

        if (allSensors != null) {
            String resultString = "";
            for (Sensor s : allSensors) {
                resultString += String.format("Name=" + s.getName());
                resultString += String.format(",Vendor=" + s.getVendor());
                resultString += String.format(",Version=" + s.getVersion());
                resultString += String.format(",MaximumRange=" + s.getMaximumRange());
                // XXX MinDelay is not in the 2.2
                //resultString += String.format(",MinDelay=" + s.getMinDelay());
                resultString += String.format(",Power=" + s.getPower());
                resultString += String.format(",Type=" + s.getType() + "\n");
            }
            return resultString;
        }
        return "";
    }


    /**
     * Get Access to 3 Axis Hardware Sensors Accelerometer, Orientation and Magnetic Field Sensors
     */
    public static class generic3AxisSensor implements SensorEventListener {
        private final SensorManager sSensorManager;
        private final Sensor sSensor;
        private final int sSensorType;
        SensorEvent sSensorEvent;

        public generic3AxisSensor(int sensorType) {
            sSensorType = sensorType;
            sSensorManager = (SensorManager)context.getSystemService(Context.SENSOR_SERVICE);
            sSensor = sSensorManager.getDefaultSensor(sSensorType);
        }

        public void onAccuracyChanged(Sensor sensor, int accuracy) {
        }

        public void onSensorChanged(SensorEvent event) {
            sSensorEvent = event;
        }

        /**
         * Enable or disable the Sensor by registering/unregistering
         */
        public void changeStatus(boolean enable) {
            if (enable) {
                sSensorManager.registerListener(this, sSensor, SensorManager.SENSOR_DELAY_NORMAL);
            } else {
                sSensorManager.unregisterListener(this, sSensor);
            }
        }

        /**
         * Read the Sensor
         */ 
        public float[] readSensor() {
            if (sSensorEvent != null) {
                return sSensorEvent.values;
            } else {
                float rv[] = { 0f, 0f, 0f };
                return rv;
            }
        }
    }

    public static generic3AxisSensor accelerometerSensor = null;
    public static generic3AxisSensor orientationSensor = null;
    public static generic3AxisSensor magneticFieldSensor = null;

    /**
     * functions for backward compatibility reasons
     */

    public static void accelerometerEnable(boolean enable) {
        if ( accelerometerSensor == null )
            accelerometerSensor = new generic3AxisSensor(Sensor.TYPE_ACCELEROMETER);
        accelerometerSensor.changeStatus(enable);
    }
    public static float[] accelerometerReading() {
        float rv[] = { 0f, 0f, 0f };
        if ( accelerometerSensor == null )
            return rv;
        return (float[]) accelerometerSensor.readSensor();
    }
    public static void orientationSensorEnable(boolean enable) {
        if ( orientationSensor == null )
            orientationSensor = new generic3AxisSensor(Sensor.TYPE_ORIENTATION);
        orientationSensor.changeStatus(enable);
    }
    public static float[] orientationSensorReading() {
        float rv[] = { 0f, 0f, 0f };
        if ( orientationSensor == null )
            return rv;
        return (float[]) orientationSensor.readSensor();
    }
    public static void magneticFieldSensorEnable(boolean enable) {
        if ( magneticFieldSensor == null )
            magneticFieldSensor = new generic3AxisSensor(Sensor.TYPE_MAGNETIC_FIELD);
        magneticFieldSensor.changeStatus(enable);
    }
    public static float[] magneticFieldSensorReading() {
        float rv[] = { 0f, 0f, 0f };
        if ( magneticFieldSensor == null )
            return rv;
        return (float[]) magneticFieldSensor.readSensor();
    }

    static public DisplayMetrics metrics = new DisplayMetrics();

    /**
     * Get display DPI.
     */
    public static int getDPI() {
        // AND: Shouldn't have to get the metrics like this every time...
        PythonActivity.mActivity.getWindowManager().getDefaultDisplay().getMetrics(metrics);
        return metrics.densityDpi;
    }

    // /**
    //  * Show the soft keyboard.
    //  */
    // public static void showKeyboard(int input_type) {
    //     //Log.i("python", "hardware.Java show_keyword  " input_type);

    //     InputMethodManager imm = (InputMethodManager) context.getSystemService(Context.INPUT_METHOD_SERVICE);

    //     SDLSurfaceView vw = (SDLSurfaceView) view;

    //     int inputType = input_type;

    //     if (vw.inputType != inputType){
    //         vw.inputType = inputType;
    //         imm.restartInput(view);
    //         }

    //     imm.showSoftInput(view, InputMethodManager.SHOW_FORCED);
    // }

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
            state = true;
        } else {
            state = false;
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
                network_state = checkNetwork();
            }

        }, i);
    }

}
