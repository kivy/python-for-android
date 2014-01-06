package org.alanjds.sl4acompat;

import com.googlecode.android_scripting.BaseApplication;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.interpreter.InterpreterConfiguration;
import com.googlecode.android_scripting.interpreter.InterpreterConstants;
import com.googlecode.android_scripting.interpreter.InterpreterConfiguration.ConfigurationObserver;

import java.util.concurrent.CountDownLatch;

public class Sl4aCompatibleApplication extends BaseApplication implements ConfigurationObserver {

  private volatile boolean receivedConfigUpdate = true;
  private final CountDownLatch mLatch = new CountDownLatch(1);

  @Override
  public void onCreate() {
    mLatch.countDown();
  }

  @Override
  public void onConfigurationChanged() {  }

  public boolean readyToStart() {
    try {
      mLatch.await();
    } catch (InterruptedException e) {
      Log.e(e);
    }
    return receivedConfigUpdate;
  }

}
