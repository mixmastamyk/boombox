
Boom Box
=============

::

                 ┏┓ ┏━┓┏━┓┏┳┓┏┓ ┏━┓╻ ╻
        ╺━╸╺━╸   ┣┻┓┃ ┃┃ ┃┃┃┃┣┻┓┃ ┃┏╋┛   ╺━╸╺━╸
           ╺━╸   ┗━┛┗━┛┗━┛╹ ╹┗━┛┗━┛╹ ╹   ╺━╸

                   ╭══════════════╮
    ╭───────────┬──┴──────────────┴──┬───────────╮
    │(0) ___    │ ⯀  [:::::::] [] ( )│    ___ (0)│
    │  /:::::\  │────────────────────│  /:::::\  │
    │ |:::::::| │  │   ──    ──   │  │ |:::::::| │
    │ |:::::::| │  │ ─(⚙)────(⚙)─ │  │ |:::::::| │
    │  \:::::/  │  │────▯▯▯▯▯▯────│♫ │  \:::::/  │
    ╰────────────────────────────────┴───────────╯


This is a small cross-platform audio-file player module,
useful for plain-to-fancy system sound events, rings, beeps, and the like.
I couldn't find a good one for this.
"playsound" was very close at first glance but had a number of issues and
has not been updated in a while.

BoomBox can wait for the file to finish or play in the background.
It tries hard to support Windows, Mac, and Linux, and mostly succeeds.
Though you could play an eight-minute Grateful Dead jam with it,
you probably wouldn't want to.


.. ~ It's a one file pure-python module that can easily be copied into a project
.. ~ if need be.   NOT ANYMORE
.. ~ ┏┓ ┏━┓┏━┓┏┳┓┏┓ ┏━┓╻ ╻
.. ~ ┣┻┓┃ ┃┃ ┃┃┃┃┣┻┓┃ ┃┏╋┛
.. ~ ┗━┛┗━┛┗━┛╹ ╹┗━┛┗━┛╹ ╹


Usage
-------------------

Quick start—a cross-platform player looks like this:

.. code-block:: python

    from boombox import BoomBox  # power on

    boombox = BoomBox("There's_no_stoppin_us.ogg")  # load cassette

    boombox.play()  # hit the ⏯ button


The play function also returns the instance,
so if in a hurry one could do:

.. code-block:: python

    boombox = BoomBox(slow_jam).play()  # or
    BoomBox(slow_jam).play()


The latter less efficient for multiple calls, of course.
There are a number of other keyword parameters that can be passed.
Such as:

- ``wait``
- ``timeout_ms``
- ``duration_ms``
- ``binary_path`` (ChildBoomBox only, to a CLI player)

Not all arguments are supported on every implementation,
but they will not balk if given.


Implementations
-------------------

There are a number of underlying implementations if you'd like to pick a
specific one and bypass the platform default:

- Windows

  - WinBoomBox (default, wav only)
  - PyAudioBoomBox - `PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_ (wav only)
  - ChildBoomBox - Command-line player (powershell, others)

.. ~ spacer

- Mac OSX:

  - MacOSBoomBox - `PyObjc <https://pypi.org/project/pyobjc/>`_ (default, multiformat)
  - PyAudioBoomBox - `PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_ (wav only)
  - ChildBoomBox - Command-line player (afplay, others)

.. ~ spacer

- POSIX:

  - GstBoomBox - `Gstreamer <https://gstreamer.freedesktop.org/documentation/installing/on-linux.html>`_
    (default, multiformat)
  - PyAudioBoomBox - `PyAudio <https://people.csail.mit.edu/hubert/pyaudio/docs/>`_ (wav only)
  - ChildBoomBox - Command-line player (paplay, aplay, others)


Simply add an import to your script to choose a different one:

.. code-block:: python

    from boombox import PyAudioBoomBox as BoomBox


You may have to install one of the audio libraries above for Boom Box to work.

::

    ⏵ pip install --user boombox[all]  # or pyaudio, pyobjc, pygobject, etc


Playback Control
-------------------

::

    ╭───────────────────────────────────────────╮
    │ ╭───────────────────────────────────────╮ │
    │ │ ╭───────────────────────────────────╮ │ │
    │ │ │ /\ :  Electric Boogaloo     90 min│ │ │
    │ │ │/──\: .....................  NR [✓]│ │ │
    │ │ ╰───────────────────────────────────╯ │ │
    │ │      //─\\   ╭....:....╮   //─\\      │ │
    │ │     ││( )││  │)       (│  ││( )││     │ │
    │ │      \\─//   ╰....:....╯   \\─//      │ │
    │ │       _ _ ._  _ _ .__|_ _.._  _       │ │
    │ │      (_(_)│ |(_(/_│  │_(_||_)(/_      │ │
    │ │               low noise   |           │ │
    │ ╰─────── ─────────────────────── ───────╯ │
    │        /    []             []    \        │
    │       /  ()                   ()  \       │
    ╰──────/─────────────────────────────\──────╯


A simple playback interface is returned by the instance:

.. code-block:: python

    boombox.stop()  # Enough!
    boombox.play()  # One more time!


Tone Generation
-------------------

Tones are generated like this:

.. code-block:: python

        boombox.play_tone(frequency_hz, duration_ms, volume=.1)


::

    ▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
    ╲▂▂▂▂╱╲▂▂▂▂╱╲▂▂▂
    ▔╲▂▂▂╱▔╲▂▂▂╱▔╲▂▂
    ▔▔╲▂▂╱▔▔╲▂▂╱▔▔╲▂
    ▔▔▔╲▂╱▔▔▔╲▂╱▔▔▔╲
    ▔▔▔▔╲╱▔▔▔▔╲╱▔▔▔▔
    ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔

::

    ┏━┓╻ ╻╻ ╻┏━╸┏━┓╻
    ┗━┓┣━┫┗┳┛┣╸ ┗━┓╹
    ┗━┛╹ ╹ ╹ ┗━╸┗━┛╹

