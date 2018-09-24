# This module is, as much a possible, a clone of the pygame
# mixer api.

import android._android_sound as sound
import time
import threading
import os

condition = threading.Condition()


def periodic():
    for i in range(0, num_channels):
        if i in channels:
            channels[i].periodic()


num_channels = 8
reserved_channels = 0


def init(frequency=22050, size=-16, channels=2, buffer=4096):
    return None


def pre_init(frequency=22050, size=-16, channels=2, buffersize=4096):
    return None


def quit():
    stop()
    return None


def stop():
    for i in range(0, num_channels):
        sound.stop(i)


def pause():
    for i in range(0, num_channels):
        sound.pause(i)


def unpause():
    for i in range(0, num_channels):
        sound.unpause(i)


def get_busy():
    for i in range(0, num_channels):
        if sound.busy(i):
            return True

    return False


def fadeout(time):
    # Fadeout doesn't work - it just immediately stops playback.
    stop()


# A map from channel number to Channel object.
channels = {}


def set_num_channels(count):
    global num_channels
    num_channels = count


def get_num_channels(count):
    return num_channels


def set_reserved(count):
    global reserved_channels
    reserved_channels = count


def find_channel(force=False):

    busy = []

    for i in range(reserved_channels, num_channels):
        c = Channel(i)

        if not c.get_busy():
            return c

        busy.append(c)

    if not force:
        return None

    busy.sort(key=lambda x: x.play_time)

    return busy[0]


class ChannelImpl(object):

    def __init__(self, id):
        self.id = id
        self.loop = None
        self.queued = None

        self.play_time = time.time()

    def periodic(self):
        qd = sound.queue_depth(self.id)

        if qd < 2:
            self.queued = None

        if self.loop is not None and sound.queue_depth(self.id) < 2:
            self.queue(self.loop, loops=1)

    def play(self, s, loops=0, maxtime=0, fade_ms=0):
        if loops:
            self.loop = s

        sound.play(self.id, s.file, s.serial)

        self.play_time = time.time()

        with condition:
            condition.notify()

    def seek(self, position):
        sound.seek(self.id, position)

    def stop(self):
        self.loop = None
        sound.stop(self.id)

    def pause(self):
        sound.pause(self.id)

    def unpause(self):
        sound.pause(self.id)

    def fadeout(self, time):
        # No fadeout
        self.stop()

    def set_volume(self, left, right=None):
        sound.set_volume(self.id, left)

    def get_volume(self):
        return sound.get_volume(self.id)

    def get_busy(self):
        return sound.busy(self.id)

    def get_sound(self):
        is_busy = sound.busy(self.id)
        if not is_busy:
            return
        serial = sound.playing_name(self.id)
        if not serial:
            return
        return sounds.get(serial, None)

    def queue(self, s):
        self.loop = None
        self.queued = s

        sound.queue(self.id, s.what, s.serial)

        with condition:
            condition.notify()

    def get_queue(self):
        return self.queued

    def get_pos(self):
        return sound.get_pos(self.id)/1000.

    def get_length(self):
        return sound.get_length(self.id)/1000.


def Channel(n):
    """
    Gets the channel with the given number.
    """

    rv = channels.get(n, None)
    if rv is None:
        rv = ChannelImpl(n)
        channels[n] = rv

    return rv


sound_serial = 0
sounds = {}


class Sound(object):

    def __init__(self, what):

        # Doesn't support buffers.

        global sound_serial

        self._channel = None
        self._volume = 1.
        self.serial = str(sound_serial)
        sound_serial += 1

        if isinstance(what, file):  # noqa F821
            self.file = what
        else:
            self.file = file(os.path.abspath(what), "rb")  # noqa F821

        sounds[self.serial] = self

    def play(self, loops=0, maxtime=0, fade_ms=0):
        # avoid new play if the sound is already playing
        # -> same behavior as standard pygame.
        if self._channel is not None:
            if self._channel.get_sound() is self:
                return
        self._channel = channel = find_channel(True)
        channel.set_volume(self._volume)
        channel.play(self, loops=loops)
        return channel

    def stop(self):
        for i in range(0, num_channels):
            if Channel(i).get_sound() is self:
                Channel(i).stop()

    def fadeout(self, time):
        self.stop()

    def set_volume(self, left, right=None):
        self._volume = left
        if self._channel:
            if self._channel.get_sound() is self:
                self._channel.set_volume(self._volume)

    def get_volume(self):
        return self._volume

    def get_num_channels(self):
        rv = 0

        for i in range(0, num_channels):
            if Channel(i).get_sound() is self:
                rv += 1

        return rv

    def get_length(self):
        return 1.0


music_channel = Channel(256)
music_sound = None


class music(object):

    @staticmethod
    def load(filename):

        music_channel.stop()

        global music_sound
        music_sound = Sound(filename)

    @staticmethod
    def play(loops=0, start=0.0):
        # No start.

        music_channel.play(music_sound, loops=loops)

    @staticmethod
    def rewind():
        music_channel.play(music_sound)

    @staticmethod
    def seek(position):
        music_channel.seek(position)

    @staticmethod
    def stop():
        music_channel.stop()

    @staticmethod
    def pause():
        music_channel.pause()

    @staticmethod
    def unpause():
        music_channel.unpause()

    @staticmethod
    def fadeout(time):
        music_channel.fadeout(time)

    @staticmethod
    def set_volume(value):
        music_channel.set_volume(value)

    @staticmethod
    def get_volume():
        return music_channel.get_volume()

    @staticmethod
    def get_busy():
        return music_channel.get_busy()

    @staticmethod
    def get_pos():
        return music_channel.get_pos()

    @staticmethod
    def queue(filename):
        return music_channel.queue(Sound(filename))
