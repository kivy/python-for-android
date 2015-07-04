package org.renpy.android;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.app.Activity;
import android.util.Log;

public class Action {

    static Context context;

    /* Deliver some data to someone else
    */
    static void send(String mimeType, String filename, String subject, String text, String chooser_title) {
        Intent emailIntent = new Intent(android.content.Intent.ACTION_SEND);
        emailIntent.setType(mimeType);
        /** tryied with String [] emails, but hard to code the whole C/Cython part.
          if (emails != null)
          emailIntent.putExtra(android.content.Intent.EXTRA_EMAIL, emails);
         **/
        if (subject != null)
            emailIntent.putExtra(android.content.Intent.EXTRA_SUBJECT, subject);
        if (text != null)
            emailIntent.putExtra(android.content.Intent.EXTRA_TEXT, text);
        if (filename != null)
            emailIntent.putExtra(Intent.EXTRA_STREAM, Uri.parse("file://"+ filename));
        if (chooser_title == null)
            chooser_title = "Send mail";
        context.startActivity(Intent.createChooser(emailIntent, chooser_title));
    }
}
