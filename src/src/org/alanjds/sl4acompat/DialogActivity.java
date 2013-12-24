package com.dummy.fooforandroid;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ComponentName;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.content.pm.ResolveInfo;
import android.net.Uri;
import android.os.Bundle;

import com.googlecode.android_scripting.Constants;
import com.googlecode.android_scripting.FeaturedInterpreters;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;

import java.net.URL;
import java.util.List;

public class DialogActivity extends Activity {
  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);

    String scriptName = getIntent().getStringExtra(Constants.EXTRA_SCRIPT_PATH);
    String interpreter = FeaturedInterpreters.getInterpreterNameForScript(scriptName);

    if (interpreter == null) {
      Log.e("Cannot find interpreter for script " + scriptName);
      finish();
    }

    final Intent activityIntent = new Intent();

    Intent resolveIntent = new Intent(InterpreterConstants.ACTION_DISCOVER_INTERPRETERS);
    resolveIntent.addCategory(Intent.CATEGORY_LAUNCHER);
    resolveIntent.setType(InterpreterConstants.MIME + Script.getFileExtension(this));
    List<ResolveInfo> resolveInfos = getPackageManager().queryIntentActivities(resolveIntent, 0);

    if (resolveInfos != null && resolveInfos.size() == 1) {
      ActivityInfo info = resolveInfos.get(0).activityInfo;
      activityIntent.setComponent(new ComponentName(info.packageName, info.name));
      activityIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
    } else {
      final URL url = FeaturedInterpreters.getUrlForName(interpreter);
      activityIntent.setAction(Intent.ACTION_VIEW);
      activityIntent.setData(Uri.parse(url.toString()));
    }

    AlertDialog.Builder dialog = new AlertDialog.Builder(this);
    dialog.setTitle(String.format("%s is not installed.", interpreter));
    dialog.setMessage(String
        .format("Do you want to download and install APK for %s ?", interpreter));

    DialogInterface.OnClickListener buttonListener = new DialogInterface.OnClickListener() {
      @Override
      public void onClick(DialogInterface dialog, int which) {
        if (which == DialogInterface.BUTTON_POSITIVE) {
          startActivity(activityIntent);
        }
        dialog.dismiss();
        finish();
      }
    };
    dialog.setNegativeButton("No", buttonListener);
    dialog.setPositiveButton("Yes", buttonListener);
    dialog.show();
  }

}
