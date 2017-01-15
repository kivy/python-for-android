package org.kivy.android.launcher;

import java.io.UnsupportedEncodingException;
import java.io.File;
import java.io.FileInputStream;
import java.util.Properties;

import android.util.Log;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;


/**
 * This represents a project we've scanned for.
 */
public class Project {

    public String dir = null;
    String title = null;
    String author = null;
    Bitmap icon = null;
    public boolean landscape = false;

    static String decode(String s) {
        try {
            return new String(s.getBytes("ISO-8859-1"), "UTF-8");
        } catch (UnsupportedEncodingException e) {
            return s;
        }
    }

    /**
     * Scans directory for a android.txt file. If it finds one,
     * and it looks valid enough, then it creates a new Project,
     * and returns that. Otherwise, returns null.
     */
    public static Project scanDirectory(File dir) {

        // We might have a link file.
        if (dir.getAbsolutePath().endsWith(".link")) {
            try {

                // Scan the android.txt file.
                File propfile = new File(dir, "android.txt");
                FileInputStream in = new FileInputStream(propfile);
                Properties p = new Properties();
                p.load(in);
                in.close();

                String directory = p.getProperty("directory", null);

                if (directory == null) {
                    return null;
                }

                dir = new File(directory);

            } catch (Exception e) {
                Log.i("Project", "Couldn't open link file " + dir, e);
            }
        }

        // Make sure we're dealing with a directory.
        if (! dir.isDirectory()) {
            return null;
        }

        try {

            // Scan the android.txt file.
            File propfile = new File(dir, "android.txt");
            FileInputStream in = new FileInputStream(propfile);
            Properties p = new Properties();
            p.load(in);
            in.close();

            // Get the various properties.
            String title = decode(p.getProperty("title", "Untitled"));
            String author = decode(p.getProperty("author", ""));
            boolean landscape = p.getProperty("orientation", "portrait").equals("landscape");

            // Create the project object.
            Project rv = new Project();
            rv.title = title;
            rv.author = author;
            rv.icon = BitmapFactory.decodeFile(new File(dir, "icon.png").getAbsolutePath());
            rv.landscape = landscape;
            rv.dir = dir.getAbsolutePath();

            return rv;

        } catch (Exception e) {
            Log.i("Project", "Couldn't open android.txt", e);
        }

        return null;

    }
}
