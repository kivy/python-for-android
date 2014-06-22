package org.p4a.minimal;

import android.app.NativeActivity;

public class PythonActivity extends android.app.NativeActivity {
    static {
       System.loadLibrary("python2.7");
    }
 }
