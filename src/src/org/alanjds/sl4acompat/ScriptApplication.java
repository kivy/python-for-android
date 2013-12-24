package com.dummy.fooforandroid;

import com.googlecode.android_scripting.BaseApplication;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.interpreter.InterpreterConfiguration;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterConfiguration.ConfigurationObserver;

import java.util.concurrent.CountDownLatch;

public class ScriptApplication extends BaseApplication implements ConfigurationObserver {

  private volatile boolean receivedConfigUpdate = false;
  private final CountDownLatch mLatch = new CountDownLatch(1);

  @Override
  public void onCreate() {
    mConfiguration = new InterpreterConfiguration(this);
    mConfiguration.registerObserver(this);
    mConfiguration.startDiscovering(InterpreterConstants.MIME + Script.getFileExtension(this));
  }

  @Override
  public void onConfigurationChanged() {
      receivedConfigUpdate = true;
      mLatch.countDown();
  }

  public boolean readyToStart() {
    try {
      mLatch.await();
    } catch (InterruptedException e) {
      Log.e(e);
    }
    return receivedConfigUpdate;
  }

}
