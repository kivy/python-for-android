package org.kivy.android.concurrency;

import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Created by ryan on 3/28/14.
 */
public class PythonEvent {
    private final Lock lock = new ReentrantLock();
    private final Condition cond = lock.newCondition();
    private boolean flag = false;

    public void set() {
        lock.lock();
        try {
            flag = true;
            cond.signalAll();
        } finally {
            lock.unlock();
        }
    }

    public void wait_() throws InterruptedException {
        lock.lock();
        try {
            while (!flag) {
                cond.await();
            }
        } finally {
            lock.unlock();
        }
    }

    public void clear() {
        lock.lock();
        try {
            flag = false;
            cond.signalAll();
        } finally {
            lock.unlock();
        }
    }
}
