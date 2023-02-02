Tutorial 1: Basic audio musaicing with GAMuT
=================================================

Here's a basic script that demonstrates a basic pipeline for creating an audio mosaic with **GAMuT**:

.. code:: python

   from gamut.features import Corpus, Mosaic
   
   # 1) create a corpus from source:
   corpus = Corpus(source='/path/to/source/audio/folder-or-file.wav')
   
   # 2) create a mosaic for audio target and, based on corpus:
   mosaic = Mosaic(target='/path/to/target/audio/file.wav', corpus=corpus)

   # 3) convert mosaic to audio buffer and play it:
   audio = mosaic.to_audio()
   audio.play()


.. warning::
   Doing all these steps in a single script can be computationally inefficient, as it results in 
   creating the ``Corpus`` and ``Mosaic`` from scratch, everytime the script runs.

   Therefore, it's recommended to take a more modular, `divide-and-conquer` approach, and write separate scripts for each stage of the process.