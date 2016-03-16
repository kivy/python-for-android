package org.kivy.android.concurrency;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Created by ryan on 3/28/14.
 */
public class PythonLock {
    private final Lock lock = new ReentrantLock();

    public void acquire() {
        lock.lock();
    }

    public void release() {
        lock.unlock();
    }
}
