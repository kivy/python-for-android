/*
   Simple DirectMedia Layer
   Java source code (C) 2009-2011 Sergii Pylypenko

   This software is provided 'as-is', without any express or implied
   warranty.  In no event will the authors be held liable for any damages
   arising from the use of this software.

   Permission is granted to anyone to use this software for any purpose,
   including commercial applications, and to alter it and redistribute it
   freely, subject to the following restrictions:

   1. The origin of this software must not be misrepresented; you must not
   claim that you wrote the original software. If you use this software
   in a product, an acknowledgment in the product documentation would be
   appreciated but is not required. 
   2. Altered source versions must be plainly marked as such, and must not be
   misrepresented as being the original software.
   3. This notice may not be removed or altered from any source distribution.
   */

package org.renpy.android;


import android.app.Activity;
import android.content.Context;
import android.os.Bundle;
import android.view.MotionEvent;
import android.view.KeyEvent;
import android.view.Window;
import android.view.WindowManager;
import android.media.AudioTrack;
import android.media.AudioManager;
import android.media.AudioFormat;
import java.io.*;
import java.nio.ByteBuffer;
import android.util.Log;
import java.lang.Thread;


class AudioThread {

    private PythonActivity mParent;
    private AudioTrack mAudio;
    private byte[] mAudioBuffer;
    private int mVirtualBufSize;

    public AudioThread(PythonActivity parent)
    {
        mParent = parent;
        mAudio = null;
        mAudioBuffer = null;
        nativeAudioInitJavaCallbacks();
    }

    public int fillBuffer()
    {
        if( mParent.isPaused() )
        {
            try{
                Thread.sleep(200);
            } catch (InterruptedException e) {}
        }
        else
        {
            //if( Globals.AudioBufferConfig == 0 ) // Gives too much spam to logcat, makes things worse
            //     mAudio.flush();

            mAudio.write( mAudioBuffer, 0, mVirtualBufSize );
        }

        return 1;
    }

    public int initAudio(int rate, int channels, int encoding, int bufSize)
    {
        if( mAudio == null )
        {
            channels = ( channels == 1 ) ? AudioFormat.CHANNEL_CONFIGURATION_MONO : 
                AudioFormat.CHANNEL_CONFIGURATION_STEREO;
            encoding = ( encoding == 1 ) ? AudioFormat.ENCODING_PCM_16BIT :
                AudioFormat.ENCODING_PCM_8BIT;

            mVirtualBufSize = bufSize;

            if( AudioTrack.getMinBufferSize( rate, channels, encoding ) > bufSize )
                bufSize = AudioTrack.getMinBufferSize( rate, channels, encoding );

            /**
              if(Globals.AudioBufferConfig != 0) {    // application's choice - use minimal buffer
              bufSize = (int)((float)bufSize * (((float)(Globals.AudioBufferConfig - 1) * 2.5f) + 1.0f));
              mVirtualBufSize = bufSize;
              }
             **/
            mAudioBuffer = new byte[bufSize];

            mAudio = new AudioTrack(AudioManager.STREAM_MUSIC,
                    rate,
                    channels,
                    encoding,
                    bufSize,
                    AudioTrack.MODE_STREAM );
            mAudio.play();
        }
        return mVirtualBufSize;
    }

    public byte[] getBuffer()
    {
        return mAudioBuffer;
    }

    public int deinitAudio()
    {
        if( mAudio != null )
        {
            mAudio.stop();
            mAudio.release();
            mAudio = null;
        }
        mAudioBuffer = null;
        return 1;
    }

    public int initAudioThread()
    {
        // Make audio thread priority higher so audio thread won't get underrun
        Thread.currentThread().setPriority(Thread.MAX_PRIORITY);
        return 1;
    }

    public int pauseAudioPlayback()
    {
        if( mAudio != null )
        {
            mAudio.pause();
            return 1;
        }
        return 0;
    }

    public int resumeAudioPlayback()
    {
        if( mAudio != null )
        {
            mAudio.play();
            return 1;
        }
        return 0;
    }

    private native int nativeAudioInitJavaCallbacks();
}

