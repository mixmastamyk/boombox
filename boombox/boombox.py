'''
    boombox - A simple cross-platform audio-file player module for Python.
    © 2020, Mike Miller - Released under the LGPL, version 3+.

    Inspired by Playsound.

    ::

        from boombox import BoomBox

        boombox = BoomBox(sound_file, wait=True)

        boombox.play()
        boombox.stop()

        # Shortcuts
        boombox = play(sound_file, wait=True)
'''
import logging
import os
import sys
from os.path import abspath, exists, join
from time import sleep


log = logging.getLogger(__name__)
__version__ = '0.50'


class _BoomBoxBase:
    ''' Base class for proxy control of an audio player. '''

    def play(self):
        raise NotImplementedError('play() not yet implemented.')
        return self  # convenience

    def stop(self):
        raise NotImplementedError('stop() not yet implemented.')

    def verify_file(self, path):
        ''' Check file is accessible, early on. '''
        path = abspath(path)
        if not exists(path):
            raise FileNotFoundError(repr(path))
        if not os.access(path, os.R_OK):
            raise PermissionError(repr(path))
        if not os.path.getsize(path):
            raise EOFError(repr(path))
        log.debug('verified %r', path)
        return path


class WinPlayer(_BoomBoxBase):
    ''' Play an audio file via the winsound module.

        Arguments:

            sound_file      May be a path, an alias, or bytes-like object of
                            audio data.
            wait            Wait to finish, or play in background & return now.
            is_alias        Use to inform winsound that sound_file is an alias.

        Notes:
            - https://docs.python.org/3/library/winsound.html
            - Only WAV format files are supported.
    '''
    def __init__(self, sound_file, wait=None, is_alias=None, **kwargs):
        log.debug('initializing %s', self.__class__.__name__)
        self._wait = kwargs.get('block', wait)  # compat with playsound
        import winsound  # deferred

        flags = 0  # figure flags
        if is_alias:
            log.debug('is alias: %r', sound_file)
            flags |= winsound.SND_ALIAS
        elif isinstance(sound_file, bytes):
            log.debug('audio is an in-memory bytes object.')
            flags |= winsound.SND_MEMORY
        else:
            log.debug('audio is a filename to load: %r', sound_file)
            flags |= winsound.SND_FILENAME
            sound_file = self.verify_file(sound_file)
        if not self._wait:
            log.debug('not waiting for audio to finish.')
            flags |= winsound.SND_ASYNC

        self._flags = flags
        self._kwargs = kwargs
        self._player = winsound
        self._sound_file = sound_file

    def play(self):
        log.debug('playing: %r', self._sound_file)
        self._player.PlaySound(self._sound_file, self._flags)
        return self  # convenience

    def stop(self):
        log.debug('stopping: %r', self._sound_file)
        self._player.PlaySound(None, 0)


class MacOSPlayer(_BoomBoxBase):
    ''' Play an audio file on MacOS via PyObjC.

        Arguments:

            sound_file      May be a path, an alias, or bytes-like object of
                            audio data.
            wait            Wait to finish, or play in background & return now.

        Notes:
            - pip install PyObjC
    '''
    def __init__(self, sound_file, wait=None, **kwargs):
        log.debug('initializing %s', self.__class__.__name__)
        self._sound_file = sound_file = self.verify_file(sound_file)
        self._wait = kwargs.get('block', wait)  # compat with playsound

        self._player = NSSound.alloc()
        self._player.initWithContentsOfFile_byReference_(sound_file, True)

    def play(self):
        log.debug('playing: %r', self._sound_file)
        self._player.play()
        if self._wait:
            sleep(self._player.duration())
        return self  # convenience

    def stop(self):
        log.debug('stopping: %r', self._sound_file)
        self._player.stop()


# ---- POSIX -----------------------------------------------------------------
class GstPlayer(_BoomBoxBase):
    ''' Play an audio file (ogg, wav, mp3, etc) via the Gstreamer system.

        To wait, set wait=True.
        To wait, limited to a maximum amount of time, use duration_ms.
    '''
    def __init__(self, sound_file, wait=None, duration_ms=None, **kwargs):
        from gi.repository import Gst

        log.debug('initializing %s', self.__class__.__name__)
        self._sound_file = sound_file = self.verify_file(sound_file)

        # somebody set us up the bomb!
        Gst.init(None)
        playbin = Gst.ElementFactory.make('playbin', 'playbin')
        if sound_file.startswith(('http://', 'https://')):
            playbin.props.uri = sound_file
        else:
            playbin.props.uri = 'file://' + sound_file

        self._wait = kwargs.get('block', wait)  # compat with playsound
        self._duration_ms = duration_ms
        self._gst = Gst  # constants
        self._playing = Gst.State.PLAYING
        self._stopped = Gst.State.NULL
        self._EOS = Gst.MessageType.EOS  # end of stream-kowski
        self._playbin = playbin

    def _on_message(self, bus, message):
        ''' Reset playback at end of stream. '''
        MessageType = self._gst.MessageType
        mtype = message.type
        if mtype == MessageType.EOS:
            self._playbin.set_state(self._stopped)
            log.debug('end of stream: %r', self._sound_file)
        elif mtype == MessageType.ERROR:
            self._playbin.set_state(self._stopped)
            err, debug = message.parse_error()
            log.error('%r: %r' % (err, debug))

    def play(self):
        playbin = self._playbin
        playbin.set_state(self._stopped)  # rewind
        log.debug('playing %r', self._sound_file)
        result = playbin.set_state(self._playing)
        if result != self._gst.StateChangeReturn.ASYNC:
            raise RuntimeError('playbin.set_state returned: %r' % result)

        bus = playbin.get_bus()  # listen for end
        if self._wait:
            if self._duration_ms:  #  convert to nanoseconds for gst
                timeout = self._duration_ms * 1_000_000
                log.debug('timeout is %s', timeout)
            else:  # could hang if in wrong state
                log.debug('waiting for sound to end…')
                timeout = self._gst.CLOCK_TIME_NONE

            bus.poll(self._EOS, timeout)  # wait for end
            playbin.set_state(self._stopped)
        else:
            bus.add_signal_watch()
            bus.connect('message', self._on_message)  # call back on end

    def stop(self):
        log.debug('stopping: %r', self._sound_file)
        self._playbin.set_state(self._stopped)


# ---- X-Plaform -------------------------------------------------------------
class PyAudioPlayer(_BoomBoxBase):
    ''' Play an audio file via PyAudio.

        Arguments:

            sound_file      May be a path, an alias, or bytes-like object of
                            audio data.
        Note:
            - Plays in background, no blocking support.
            - Sound file must be in WAV format.
            - https://people.csail.mit.edu/hubert/pyaudio/docs/
    '''
    def __init__(self, sound_file, wait=None, **kwargs):
        from pyaudio import PyAudio, paContinue

        self._wait = kwargs.get('block', wait)  # compat with playsound
        self._PyAudio = PyAudio
        self._pa_continue = paContinue
        self._sound_file = self.verify_file(sound_file)
        self._setup_pa()

    def _setup_pa(self):
        import wave

        self._wav_file = wav_file = wave.open(self._sound_file, 'rb')
        # hide diag output on stderr :-/
        with open(os.devnull, 'w') as devnull:
            orig_stdout_fno = os.dup(sys.stderr.fileno())
            os.dup2(devnull.fileno(), 2)
            self._pa = pa = self._PyAudio()  # <-- lots of output here :-(
            os.dup2(orig_stdout_fno, 2)

        self.stream = pa.open(
            format = pa.get_format_from_width(wav_file.getsampwidth()),
            channels = wav_file.getnchannels(),
            rate = wav_file.getframerate(),
            output = True,
            stream_callback = self._read_stream,
        )

    def _read_stream(self, in_data, frame_count, time_info, status):
        data = self._wav_file.readframes(frame_count)
        return (data, self._pa_continue)

    def play(self):
        log.debug('playing: %r', self._sound_file)
        self._wav_file.rewind()
        try:
            self.stream.start_stream()
        except OSError:
            log.warn('stream closed, restarting.')
            self._setup_pa()
            self.stream.start_stream()

        if self._wait:
            from time import sleep
            while self.stream.is_active():
                sleep(0.2)
        return self  # convenience

    def stop(self, close=True):
        log.debug('stopping: %r', self._sound_file)
        self.stream.stop_stream()
        if close:
            self.close()

    def close(self):
        log.debug('closing: %r', self._sound_file)
        try:
            self._wav_file.close()
            self.stream.close()
            self._pa.terminate()
        except AttributeError:
            pass

    def __del__(self):
        self.close()


class ChildPlayer(_BoomBoxBase):
    ''' Play an audio file with an arbitrary command-line player.

        Returns an OS process status code.
    '''
    def __init__(self, sound_file, wait=None, binary_path=None, **kwargs):
        from subprocess import Popen  # deferred

        self._sound_file = sound_file = self.verify_file(sound_file)
        self._Popen = Popen
        self._wait = kwargs.get('block', wait)  # compat with playsound
        self.failed = None
        args = []
        if not binary_path:  # find a platform default
            if os.name == 'nt':             # I'm a PC
                args.extend(
                    ('powershell', '-c', # ;
                    '(New-Object Media.SoundPlayer {sound_file!r}).PlaySync()')
                )
            elif sys.platform == 'darwin':  # Think different
                args.append('afplay')
                args.append(sound_file)
            elif os.name == 'posix':        # Tron leotards
                path = _search_path('paplay')
                if not path:
                    path = _search_path('aplay')  # try again
                args.append(path)
                args.append(sound_file)

        self._args = args = tuple(args)
        log.debug('command-line: %r', args)

    def play(self):
        log.debug('playing: %r', self._sound_file)
        # args as list, not sure why this works w/o shell:
        self._child = self._Popen(self._args)
        if self._wait:
            returncode = self._child.wait()
            log.debug('%s returned: %s', self._child, returncode)
            self.failed = bool(returncode)
        return self  # convenience

    def stop(self):
        log.debug('stopping: %r', self._sound_file)
        self._child.terminate()


def _search_path(binary):
    ''' Look for a executable on the PATH. '''
    import env

    result = None
    for path in env.PATH.list:
        binary_path = join(path, binary)
        binary_path_exists = exists(binary_path)
        if binary_path_exists:
            result = binary_path
            break

    log.debug('binary_path: %r', result)
    return result


# Assign a default Player
if os.name == 'nt':             # I'm a PC
    _example_file = 'c:/Windows/Media/Alarm08.wav'
    BoomBox = WinPlayer

elif sys.platform == 'darwin':  # Think different
    _example_file = '/System/Library/Sounds/Ping.aiff'
    try:
        log.debug('trying AppKit.NSSound…')
        from AppKit import NSSound
        BoomBox = MacOSPlayer
    except ImportError:
        log.debug('AppKit not available, falling back to subprocess…')
        BoomBox = ChildPlayer


elif os.name == 'posix':        # Tron leotards
    _example_file = '/usr/share/sounds/ubuntu/stereo/desktop-login.ogg'
    try:
        log.debug('trying gstreamer…')
        import gi
        gi.require_version('Gst', '1.0')  # shrug
        BoomBox = GstPlayer
    except ImportError:
        log.debug('python3-gi not available, trying pyaudio…')
        try:
            import pyaudio;  pyaudio  # pyflakes
            BoomBox = PyAudioPlayer
        except ImportError:
            log.debug('pyaudio not available, falling back to subprocess…')
            BoomBox = ChildPlayer


if __name__ == '__main__':
    import out
    out.configure(level='debug')

    if len(sys.argv) > 1 and sys.argv[1]:
        sound_file = sys.argv[1]
    else:
        sound_file = _example_file

    boombox = BoomBox(sound_file, wait=True)
    boombox.play()
