Tutorial 1: Basic audio musaicking with GAMuT
=================================================

Broadly speaking, the audio musaicking pipeline with **GAMuT** is quite simple:

1. Create a ``Corpus`` from one or more audio sources.
2. Create an ``Mosaic`` from one or more ``Corpus`` instances, given a `target` audio file.
3. Convert ``Mosaic`` to an ``AudioBuffer`` instance, and write it into disk as a ``.wav`` or ``.aif`` audio file.

Here's a simple script that demonstrates this basic pipeline in Python:

.. code:: python

   from gamut.features import Corpus, Mosaic
   
   # 1) create a corpus from source:
   corpus = Corpus(source='/path/to/source/audio/folder-or-file.wav')
   
   # 2) create a mosaic for audio target and, based on corpus:
   mosaic = Mosaic(target='/path/to/target/audio/file.wav', corpus=corpus)

   # 3) convert mosaic to audio buffer and play it:
   audio = mosaic.to_audio()
   audio.play()


.. hint::
   Doing all these steps in a single script can be computationally inefficient, as it results in 
   creating the ``Corpus`` and ``Mosaic`` from scratch, everytime the script runs.

   Therefore, it's recommended to take a more modular, `divide-and-conquer` approach, and write separate scripts for each stage of the process.