package org.renpy.android;

import android.media.MediaPlayer;
import android.util.Log;
import java.io.FileInputStream;
import java.io.IOException;
import java.util.HashMap;

public class RenPySound {
    
    private static class Channel implements MediaPlayer.OnCompletionListener, MediaPlayer.OnPreparedListener {

        // MediaPlayers for the currently playing and queued up
        // sounds.
        MediaPlayer player[];
        
        // Filenames for the currently playing and queued up sounds.
        String filename[];

        // Is the corresponding player prepareD?
        boolean prepared[];
        
        // The volume for the left and right channel.
        double volume;
        double secondary_volume;
        double left_volume;
        double right_volume;
        
        Channel() {
            player = new MediaPlayer[2];
            filename = new String[2];
            prepared = new boolean[2];
            
            player[0] = new MediaPlayer();
            player[1] = new MediaPlayer();

            volume = 1.0;
            secondary_volume = 1.0;
            left_volume = 1.0;
            right_volume = 1.0;            
        }

        /**
         * Queue up a sound file.
         */
        synchronized void queue(String fn, String real_fn, long base, long length) {
            MediaPlayer mp = player[1];

            mp.reset();

            try {
                FileInputStream f = new FileInputStream(real_fn);
                
                if (length >= 0) {
                    mp.setDataSource(f.getFD(), base, length);
                } else {
                    mp.setDataSource(f.getFD());
                }

                mp.setOnCompletionListener(this);
                mp.setOnPreparedListener(this);
                
                mp.prepareAsync();
                
                f.close();
            } catch (IOException e) {
                Log.w("RenPySound", e);
                return;
            }
            

            filename[1] = fn;           
            
        }

        /**
         * Play the queued-up sound.
         */
        synchronized void play() {
            MediaPlayer tmp;

            player[0].reset();
            
            tmp = player[0];
            player[0] = player[1];
            player[1] = tmp;
            
            filename[0] = filename[1];
            filename[1] = null;

            prepared[0] = prepared[1];
            prepared[1] = false;
            
            if (filename[0] != null) {
                updateVolume();

                if (prepared[0]) {                
                    player[0].start();
                }
            }
        }
        
        /**
         * Stop playback on this channel.
         */
        synchronized void stop() {
            player[0].reset();
            player[1].reset();

            filename[0] = null;
            filename[1] = null;

            prepared[0] = false;
            prepared[1] = false;
        }

        /**
         * Dequeue the queued file on this channel.
         */
        synchronized void dequeue() {
            player[1].reset();
            filename[1] = null;
            prepared[1] = false;
        }


        /**
         * Updates the volume on the playing file.
         */
        synchronized void updateVolume() {
            player[0].setVolume((float) (volume * secondary_volume * left_volume),
                                (float) (volume * secondary_volume * right_volume));
        }


        /**
         * Called to update the volume.
         */
        synchronized void set_volume(float v) {
            volume = v;
            updateVolume();
        }

        /**
         * Called to update the volume.
         */
        synchronized void set_secondary_volume(float v) {
            secondary_volume = v;
            updateVolume();
        }

        /**
         * Called to update the pan. (By setting up the fractional
         * volume.)
         */
        synchronized void set_pan(float pan) {
            if (pan < 0) {
                left_volume = 1.0;
                right_volume = 1.0 + pan;
            } else {
                left_volume = 1.0 - pan;
                right_volume = 1.0;
            }
            
            updateVolume();
         }

        synchronized void pause() {
            if (filename[0] != null) {
                player[0].pause();
            }
        }

        synchronized void unpause() {
            if (filename[0] != null) {
                player[0].start();
            }
        }

        synchronized public void onPrepared(MediaPlayer mp) {
            if (mp == player[0]) {
                prepared[0] = true;
                player[0].start();
            }

            if (mp == player[1]) {
                prepared[1] = true;
            }
        }
                
        /**
         * Called on completion.
         */
        synchronized public void onCompletion(MediaPlayer mp) {
            if (mp == player[0]) {
                play();
            }
        }

        
    }

    // A map from channel number to channel object.
    static HashMap<Integer, Channel> channels = new HashMap<Integer, Channel>();

    /**
     * Gets the Channel object for the numbered channel, returning a
     * new channel object as necessary.
     */
    static Channel getChannel(int num) {
        Channel rv = channels.get(num);

        if (rv == null) {
            rv = new Channel();
            channels.put(num, rv);
        }

        return rv;
    }

    static void queue(int channel, String filename, String real_fn, long base, long length) {        
        Channel c = getChannel(channel);
        c.queue(filename, real_fn, base, length);
        if (c.filename[0] == null) {
          c.play();
        }
        
    }

    static void play(int channel,
                     String filename,
                     String real_fn,
                     long base,
                     long length) {

        Channel c = getChannel(channel);
        c.queue(filename, real_fn, base, length);
        c.play();
    }

    static void stop(int channel) {
        Channel c = getChannel(channel);
        c.stop();
    }

    static void dequeue(int channel) {
        Channel c = getChannel(channel);
        c.dequeue();
    }


    static String playing_name(int channel) {
        Channel c = getChannel(channel);
        if (c.filename[0] == null) {
            return "";
        }

        return c.filename[0];
    }

    static int queue_depth(int channel) {
        Channel c = getChannel(channel);

        if (c.filename[0] == null) return 0;
        if (c.filename[1] == null) return 1;
        return 2;
    }

    static void set_volume(int channel, float v) {
        Channel c = getChannel(channel);
        c.set_volume(v);
    }

    static void set_secondary_volume(int channel, float v) {
        Channel c = getChannel(channel);
        c.set_secondary_volume(v);
    }

    static void set_pan(int channel, float pan) {
        Channel c = getChannel(channel);
        c.set_pan(pan);
    }

    static void pause(int channel) {
        Channel c = getChannel(channel);
        c.pause();
    }

    static void unpause(int channel) {
        Channel c = getChannel(channel);
        c.unpause();
    }

    static {
        new MediaPlayer();
    }
    
}