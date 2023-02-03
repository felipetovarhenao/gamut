Tutorial 4: Converting mosaic to audio
========================================================

Once a ``Mosaic`` has been saved as a `.gamut` file, we can load it and generate the actual `mosaic` as `audio`, based on different 
audio control parameters we pass to the ``to_audio()`` method. More on this later on, but for now here's an example 
of how we can read and write an `audio mosaic` to disk:

.. code:: python

    from gamut.features import Mosaic

    # 1) read previously created mosaic
    mosaic = Mosaic()
    mosaic.read('/path/to/my_mosaic.gamut')

    # 2) convert to audio and write to disk as .wav
    audio = mosaic.to_audio()
    audio.write('/path/to/audio.wav')

.. hint::
    The ``to_audio()`` method returns a :class:`gamut.audio.AudioBuffer` instance, which will be discussed in later tutorials.

    