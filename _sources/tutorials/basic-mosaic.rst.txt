Tutorial 3: Creating an audio mosaic 
=================================================

A ``Mosaic`` represents a **blueprint** from which an audio mosaic can be synthesized.
Given an input audio target file path and a ``Corpus`` instance, a virtual representation of 
an audio mosaic is built, to be later converted to audio with the ``to_audio()`` method.

By `blueprint`, it's meant that a ``Mosaic`` instance generates and stores the necessary
information to synthesize an audio mosaic, but **does not** automatically generate the mosaic as an audio file. 

This allows the user to create different versions, based on the audio parameters passed to the 
``to_audio()`` method, which in turn returns an ``AudioBuffer`` instance.

Here's a simple script showing how to write a `mosaic` as a ``.gamut`` file:

.. code:: python

    from gamut.features import Corpus, Mosaic

    # 1) read corpus from a previously created .gamut file
    corpus = Corpus()
    corpus.read('path/to/my_corpus.gamut')

    # 2) create a mosaic for a given an audio target and a corpus
    mosaic = Mosaic(target='/path/to/target/audio/file.wav', corpus=corpus)

    # 3) write mosaic to disk as a .gamut file
    mosaic.write('path/to/my_mosaic.gamut')

Next time we want to use this mosaic, we simply read it from disk:

.. code:: python

    from gamut.features import Mosaic

    mosaic = Mosaic().read('path/to/my_corpus.gamut')