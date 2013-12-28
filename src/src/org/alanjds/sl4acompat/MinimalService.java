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

import com.googlecode.android_scripting.AndroidProxy;
import com.googlecode.android_scripting.ForegroundService;
import com.googlecode.android_scripting.Log;
import com.googlecode.android_scripting.NotificationIdFactory;
import com.googlecode.android_scripting.jsonrpc.RpcReceiverManager;

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
		Log.v('Starting MinimalService');
		super.onStart(intent, startId);

		Log.v('Starting AndroidProxy');
		mProxy = new AndroidProxy(this, intent, true);
		mProxy.startLocal();

		String host = mProxy.getAddress().getAddress();
		String port = mProxy.getAddress().getPort().toString();
		String handshake = mProxy.getSecret();
		Log.v(String.format("AndroidProxy at: %s @ %s:%s", handshake, host, port));

		Intent netaddress = new Intent(this, "org.alanjds.sl4acompat.STORE_RPC_NETADDRESS");
		netaddress.putExtra("host", host);
		netaddress.putExtra("port", port);
		netaddress.putExtra("handshake", handshake);
		sendBroadcast(netaddress);

		mLatch.countDown();
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
