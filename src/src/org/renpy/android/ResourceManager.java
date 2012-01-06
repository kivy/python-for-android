/**
 * This class takes care of managing resources for us. In our code, we
 * can't use R, since the name of the package containing R will
 * change. (This same code is used in both org.renpy.android and
 * org.renpy.pygame.) So this is the next best thing.
 */

package org.renpy.android;

import android.app.Activity;
import android.content.res.Resources;
import android.view.View;

public class ResourceManager {

    private Activity act;
    private Resources res;
    
    public ResourceManager(Activity activity) {
        act = activity;
        res = act.getResources();
    }

    public int getIdentifier(String name, String kind) {
        return res.getIdentifier(name, kind, act.getPackageName());
    }
        
    public String getString(String name) {

        try {
            return res.getString(getIdentifier(name, "string"));
        } catch (Exception e) {
            return null;
        }
    }

    public View inflateView(String name) {
        int id = getIdentifier(name, "layout");
        return act.getLayoutInflater().inflate(id, null);
    }

    public View getViewById(View v, String name) {
        int id = getIdentifier(name, "id");
        return v.findViewById(id);
    }
    
}