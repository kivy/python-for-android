/*
 * Copyright (C) 2010 Google Inc.
 * Copyright (C) 2014 Alan Justino
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not
 * use this file except in compliance with the License. You may obtain a copy of
 * the License at
 * 
 * http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */

package org.alanjds.sl4acompat;

import android.app.Notification;
import android.app.PendingIntent;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.os.AsyncTask;

import com.googlecode.android_scripting.AndroidProxy;
import com.googlecode.android_scripting.ForegroundService;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.NotificationIdFactory;
import com.googlecode.android_scripting.jsonrpc.RpcReceiverManager;

import java.net.InetSocketAddress;
import java.util.concurrent.CountDownLatch;

/**
 * A service that allows scripts and the RPC server to run in the background.
 * 
 * @author Alexey Reznichenko (alexey.reznichenko@gmail.com)
 * @author Manuel Naranjo (manuel@aircable.net)
 * @author Alan Justino (alan.justino@yahoo.com.br)
 */
public class MinimalService extends ForegroundService {
	private final static int NOTIFICATION_ID = NotificationIdFactory.create();
	private final CountDownLatch mLatch = new CountDownLatch(1);
	private final IBinder mBinder;

	//private InterpreterConfiguration mInterpreterConfiguration;
	private RpcReceiverManager mFacadeManager;
	private AndroidProxy mProxy;
	private InetSocketAddress mAddressWithPort;
	private String mProxyAddress;

	public class LocalBinder extends Binder {
		public MinimalService getService() {
			return MinimalService.this;
		}
	}

	public MinimalService() {
		super(NOTIFICATION_ID);
		mBinder = new LocalBinder();
	}

	@Override
	public IBinder onBind(Intent intent) {
		return mBinder;
	}

	@Override
	public void onCreate() {
		super.onCreate();
	}

	@Override
	public void onStart(Intent intent, final int startId) {
		Log.v("Starting MinimalService");
		super.onStart(intent, startId);

		mProxy = new AndroidProxy(this, null, true);

		Log.v("Starting ProxyStarter");
		mProxyAddress = new ProxyStarter().execute(""); // Thread, as cannot be on UI thread
		Log.v("Finished ProxyStarter");

		mLatch.countDown();
	}

	private class ProxyStarter extends AsyncTask<String, Void, String> {

		@Override
		protected String doInBackground(String... params) {
			Log.v("Starting AndroidProxy");
			mAddressWithPort = mProxy.startLocal();
			Log.v("Started AndroidProxy");

			String host = mAddressWithPort.getAddress().getHostAddress();
			Integer iPort = mAddressWithPort.getPort();
			String port = iPort.toString();
			String handshake = mProxy.getSecret();
			String proxyAddress = String.format("%s@%s:%s", handshake, host, port);
			Log.v(String.format("AndroidProxy at: %s @ %s:%s", handshake, host, port));

			Intent netaddress = new Intent("org.alanjds.sl4acompat.STORE_RPC_NETADDRESS");
			netaddress.putExtra("host", host);
			netaddress.putExtra("port", port);
			netaddress.putExtra("handshake", handshake);
			sendBroadcast(netaddress);
			Log.v("Sent 'org.alanjds.sl4acompat.STORE_RPC_NETADDRESS'");

			return proxyAddress;
		}

		@Override
		protected void onPostExecute(String result) {
		    //TextView txt = (TextView) findViewById(R.id.output);
		    //txt.setText("Executed"); // txt.setText(result);
		    //// might want to change "executed" for the returned string passed
		    //// into onPostExecute() but that is upto you
		}

		@Override
		protected void onPreExecute() {}

		@Override
		protected void onProgressUpdate(Void... values) {}
	}

	RpcReceiverManager getRpcReceiverManager() throws InterruptedException {
		mLatch.await();
		if (mFacadeManager==null) { // Facade manage may not be available on startup.
			mFacadeManager = mProxy.getRpcReceiverManagerFactory()
			.getRpcReceiverManagers().get(0);
		}
		return mFacadeManager;
	}

	@Override
	protected Notification createNotification() {
		PendingIntent contentIntent = PendingIntent.getService(this, 0, new Intent(), 0);
		// This contentIntent is a noop.

		Notification notification = new Notification();
			//.setContentTitle("SL4A Facade")
			//.setContentText("minimal SL4A facade running")
			//.setContentIntent(contentIntent)
			//.build();

		//NotificationManager notificationManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
		notification.flags |= Notification.FLAG_AUTO_CANCEL;	// hide the notification after its selected

		//notificationManager.notify(0, notification);
		return notification;
	}
}
