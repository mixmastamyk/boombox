
Boom Box
=============

This is a short cross-platform audio-file player module,
useful for plain to fancy system sound events, rings, beeps, and the like.
It's a one file pure-python module that can easily be copied into a project
if need be.

(While you could play an eight-minute Grateful Dead tune with it,
you probably wouldn't want to.)

I couldn't find a good module for this.
"playsound" was quite close but had a number of issues and appeared abandoned.
So, I whipped this up with heavy inspiration.


Usage
-------------------

.. code-block:: python

    from boombox import play

    path = '/usr/share/sounds/ubuntu/stereo/phone-outgoing-busy.ogg'

    play(path)


There are a number of parameters that can be passed.
Such as:

- wait
- timeout_ms
- duration_ms

Not all arguments are supported on every implementation.


Support
-------------------

Boom Box supports:

- Windows

  - WinAPI (default)
  - `PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_
  - Command-line player

- Mac OSX, via:

  - `PyObjc <https://pypi.org/project/pyobjc/>`_ (default)
  - `PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_
  - Command-line player

- POSIX, via:

  - `Gstreamer <https://gstreamer.freedesktop.org/documentation/installing/on-linux.html>`_
    (default)
  - `PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_
  - Command-line player (paplay, others)

You may have to install one of these audio libraries for Boom Box to work.
Check their documentation for details.



Implementations
-------------------

There are a number of implementations if you'd like to bypass the chosen
default:

.. code-block:: python

    play_gstreamer(sound_file, block=None, timeout_ms=None)
    play_macos(sound_file)
    play_oss(sound_file)        # needs work
    play_pyaudio(sound_file)    # wav only
    play_windows(sound_file)    # wav only

    # CLI players
    play_subprocess(sound_file, binary_path=None)
    play_linux_call(sound_file, binary_path='paplay')
    play_macos_call(sound_file, binary_path='afplay')

    # add this to your script:
    from boombox import play_linux_call as play


Playback Control
-------------------

A very rudimentary playback interface is returned by the play functions if
one needs a bit of control:

.. code-block:: python

    boombox = play(path)

    boombox.stop()  # Enough!
    boombox.play()  # One more time!
