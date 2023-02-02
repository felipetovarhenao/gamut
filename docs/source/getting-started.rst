Getting started
===============

Broadly speaking, the audio musaicing pipeline with **GAMuT** is quite simple:

1. Create a ``Corpus`` from one or more audio sources.
2. Create an ``Mosaic`` from one or more ``Corpus`` instances, given a `target` audio file.
3. Convert ``Mosaic`` to an ``AudioBuffer`` instance, and write it into disk as a ``.wav`` or ``.aif`` audio file.

Here are some user-friendly tutorials to get started with **GAMuT**:

.. toctree::
   :maxdepth: 2
   :caption: Tutorials:

   tutorials/basic-pipeline
   tutorials/basic-corpus
   tutorials/basic-mosaic
   tutorials/basic-audio
   tutorials/audio-params
   tutorials/corpus-features
