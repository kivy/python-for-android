
package net.inclem.android;

import org.libsdl.app.SDLActivity;

public class NewPythonActivity extends SDLActivity {
    
    // This is just overrides the normal SDLActivity, which just loads
    // SDL2 and main
    protected String[] getLibraries() {
        return new String[] {
            "SDL2",
            "SDL2_image",
            "SDL2_mixer",
            "SDL2_ttf",
            "python2.7",
            "main"
        };
    }
    
    public void loadLibraries() {
        // AND: This should probably be replaced by a call to super
        for (String lib : getLibraries()) {
            System.loadLibrary(lib);
        }
        
    }

}
