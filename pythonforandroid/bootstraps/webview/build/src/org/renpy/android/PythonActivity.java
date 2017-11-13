package org.renpy.android;

import android.util.Log;

class PythonActivity extends org.kivy.android.PythonActivity {
    static {
        Log.w("PythonActivity", "Accessing org.renpy.android.PythonActivity " 
                                + "is deprecated and will be removed in a "
                                + "future version. Please switch to "
                                + "org.kivy.android.PythonActivity.");
    }
}
