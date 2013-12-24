// Copyright 2010 Google Inc. All Rights Reserved.

package com.dummy.fooforandroid;

import android.content.Context;
import android.content.res.Resources;

public class Script {

  public final static int ID = R.raw.script;

  public static String sFileName;

  public static String getFileName(Context context) {
    if (sFileName == null) {
      Resources resources = context.getResources();
      String name = resources.getText(ID).toString();
      sFileName = name.substring(name.lastIndexOf('/') + 1, name.length());
    }
    return sFileName;
  }

  public static String getFileExtension(Context context) {
    if (sFileName == null) {
      getFileName(context);
    }
    int dotIndex = sFileName.lastIndexOf('.');
    if (dotIndex == -1) {
      return null;
    }
    return sFileName.substring(dotIndex);
  }

}
