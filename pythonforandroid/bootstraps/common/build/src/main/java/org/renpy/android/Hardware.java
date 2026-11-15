package org.renpy.android;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.net.wifi.ScanResult;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.util.DisplayMetrics;
import android.view.View;
import android.view.inputmethod.InputMethodManager;

import org.kivy.android.PythonActivity;

import java.util.List;

/**
 * Methods that are expected to be called via JNI, to access the device's non-screen hardware. (For
 * example, the vibration and accelerometer.)
 */
public class Hardware {

    // The context.
    public static Context context;
    public static View view;
    public static final float defaultRv[] = {0f, 0f, 0f};

    private static Context getContext() {
        if (context != null) return context;
        return PythonActivity.mActivity;
    }

    private static View getView() {
        if (view != null) return view;
        return PythonActivity.mActivity.getWindow().getDecorView();
    }

    /** Vibrate for s seconds. */
    public static void vibrate(double s) {
        Vibrator v = (Vibrator) getContext().getSystemService(Context.VIBRATOR_SERVICE);
        if (v != null) {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                v.vibrate(
                        VibrationEffect.createOneShot(
                                (long) (1000 * s), VibrationEffect.DEFAULT_AMPLITUDE));
            } else {
                v.vibrate((long) (1000 * s));
            }
        }
    }

    /** Get an Overview of all Hardware Sensors of an Android Device */
    public static String getHardwareSensors() {
        SensorManager sm = (SensorManager) getContext().getSystemService(Context.SENSOR_SERVICE);
        List<Sensor> allSensors = sm.getSensorList(Sensor.TYPE_ALL);

        if (allSensors != null) {
            StringBuilder resultString = new StringBuilder();
            for (Sensor s : allSensors) {
                resultString.append(
                        String.format(
                                "Name=%s,Vendor=%s,Version=%d,MaximumRange=%f,Power=%f,Type=%d\n",
                                s.getName(),
                                s.getVendor(),
                                s.getVersion(),
                                s.getMaximumRange(),
                                s.getPower(),
                                s.getType()));
            }
            // XXX MinDelay is not in the 2.2
            // resultString.append(String.format(",MinDelay=" + s.getMinDelay()));
            return resultString.toString();
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
            sSensorManager = (SensorManager) getContext().getSystemService(Context.SENSOR_SERVICE);
            sSensor = sSensorManager.getDefaultSensor(sSensorType);
        }

        public void onAccuracyChanged(Sensor sensor, int accuracy) {}

        public void onSensorChanged(SensorEvent event) {
            sSensorEvent = event;
        }

        /** Enable or disable the Sensor by registering/unregistering */
        public void changeStatus(boolean enable) {
            if (sSensor == null) return;
            if (enable) {
                sSensorManager.registerListener(this, sSensor, SensorManager.SENSOR_DELAY_NORMAL);
            } else {
                sSensorManager.unregisterListener(this, sSensor);
            }
        }

        /** Read the Sensor */
        public float[] readSensor() {
            if (sSensorEvent != null) {
                return sSensorEvent.values;
            } else {
                return defaultRv;
            }
        }
    }

    public static generic3AxisSensor accelerometerSensor = null;
    public static generic3AxisSensor orientationSensor = null;
    public static generic3AxisSensor magneticFieldSensor = null;

    /** functions for backward compatibility reasons */
    public static void accelerometerEnable(boolean enable) {
        if (accelerometerSensor == null)
            accelerometerSensor = new generic3AxisSensor(Sensor.TYPE_ACCELEROMETER);
        accelerometerSensor.changeStatus(enable);
    }

    public static float[] accelerometerReading() {
        if (accelerometerSensor == null) return defaultRv;
        return accelerometerSensor.readSensor();
    }

    public static void orientationSensorEnable(boolean enable) {
        if (orientationSensor == null)
            orientationSensor = new generic3AxisSensor(Sensor.TYPE_ORIENTATION);
        orientationSensor.changeStatus(enable);
    }

    public static float[] orientationSensorReading() {
        if (orientationSensor == null) return defaultRv;
        return orientationSensor.readSensor();
    }

    public static void magneticFieldSensorEnable(boolean enable) {
        if (magneticFieldSensor == null)
            magneticFieldSensor = new generic3AxisSensor(Sensor.TYPE_MAGNETIC_FIELD);
        magneticFieldSensor.changeStatus(enable);
    }

    public static float[] magneticFieldSensorReading() {
        if (magneticFieldSensor == null) return defaultRv;
        return magneticFieldSensor.readSensor();
    }

    public static DisplayMetrics metrics = new DisplayMetrics();

    /** Get display DPI. */
    public static int getDPI() {
        if (PythonActivity.mActivity != null) {
            // AND: Shouldn't have to get the metrics like this every time...
            PythonActivity.mActivity.getWindowManager().getDefaultDisplay().getMetrics(metrics);
            return metrics.densityDpi;
        }
        return 160;
    }

    // /**
    //  * Show the soft keyboard.
    //  */
    // public static void showKeyboard(int input_type) {
    //     //Log.i("python", "hardware.Java show_keyword  " input_type);

    //     InputMethodManager imm = (InputMethodManager)
    // context.getSystemService(Context.INPUT_METHOD_SERVICE);

    //     SDLSurfaceView vw = (SDLSurfaceView) view;

    //     int inputType = input_type;

    //     if (vw.inputType != inputType){
    //         vw.inputType = inputType;
    //         imm.restartInput(view);
    //         }

    //     imm.showSoftInput(view, InputMethodManager.SHOW_FORCED);
    // }

    /** Hide the soft keyboard. */
    public static void hideKeyboard() {
        InputMethodManager imm =
                (InputMethodManager) getContext().getSystemService(Context.INPUT_METHOD_SERVICE);
        if (imm != null) {
            imm.hideSoftInputFromWindow(getView().getWindowToken(), 0);
        }
    }

    /** Scan WiFi networks */
    static List<ScanResult> latestResult;

    public static void enableWifiScanner() {
        IntentFilter i = new IntentFilter();
        i.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION);

        getContext()
                .registerReceiver(
                        new BroadcastReceiver() {

                            @Override
                            public void onReceive(Context c, Intent i) {
                                // Code to execute when SCAN_RESULTS_AVAILABLE_ACTION event occurs
                                try {
                                    WifiManager w =
                                            (WifiManager)
                                                    c.getApplicationContext()
                                                            .getSystemService(Context.WIFI_SERVICE);
                                    if (w != null) {
                                        latestResult = w.getScanResults(); // Returns a <list> of
                                        // scanResults
                                    }
                                } catch (SecurityException e) {
                                    // Modern Android requires ACCESS_FINE_LOCATION to scan WiFi
                                }
                            }
                        },
                        i);
    }

    public static String scanWifi() {

        // Now you can call this and it should execute the broadcastReceiver's
        // onReceive()
        if (latestResult != null) {

            StringBuilder latestResultString = new StringBuilder();
            for (ScanResult result : latestResult) {
                latestResultString.append(
                        String.format("%s\t%s\t%d\n", result.SSID, result.BSSID, result.level));
            }

            return latestResultString.toString();
        }

        return "";
    }

    /** network state */
    public static boolean network_state = false;

    /**
     * Check network state directly
     *
     * <p>(only one connection can be active at a given moment, detects all network type) Using
     * NetworkCapabilities for API >= 23, falling back to activeNetworkInfo for older devices.
     */
    public static boolean checkNetwork() {
        final ConnectivityManager conMgr =
                (ConnectivityManager) getContext().getSystemService(Context.CONNECTIVITY_SERVICE);
        if (conMgr == null) return false;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            Network network = conMgr.getActiveNetwork();
            if (network == null) return false;
            NetworkCapabilities capabilities = conMgr.getNetworkCapabilities(network);
            return capabilities != null
                    && (capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
                            || capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)
                            || capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET));
        } else {
            final NetworkInfo activeNetwork = conMgr.getActiveNetworkInfo();
            return activeNetwork != null && activeNetwork.isConnected();
        }
    }

    /** To receive network state changes */
    public static void registerNetworkCheck() {
        network_state = checkNetwork();

        ConnectivityManager conMgr =
                (ConnectivityManager) getContext().getSystemService(Context.CONNECTIVITY_SERVICE);
        if (conMgr == null) return;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            conMgr.registerDefaultNetworkCallback(
                    new ConnectivityManager.NetworkCallback() {
                        @Override
                        public void onAvailable(Network network) {
                            network_state = true;
                        }

                        @Override
                        public void onLost(Network network) {
                            network_state = false;
                        }
                    });
        } else {
            IntentFilter i = new IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION);
            getContext()
                    .registerReceiver(
                            new BroadcastReceiver() {
                                @Override
                                public void onReceive(Context c, Intent i) {
                                    network_state = checkNetwork();
                                }
                            },
                            i);
        }
    }
}
