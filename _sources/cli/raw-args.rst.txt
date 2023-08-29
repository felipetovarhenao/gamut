.. role:: marked
    :class: marked

Option 1: Direct input arguments
=================================

The quickest, but perhaps **least efficient** way of doing audio musaicking with **GAMuT**'s command-line interface is by using `direct input arguments`. Let's start with the most basic example:

.. code:: shell

   gamut --target /path/to/audio/target.wav --source /path/to/audio/source.wav

This will generate an audio mosaic for the given ``--target``, based on the given ``--source``. The final audio output will be written to disk as ``gamut-audio.wav`` in the current directory.
To play back the audio at the end of the process, we can use the ``--play`` argument, and also specify the audio output filename path, with the ``--audio`` argument.

.. code:: shell

   gamut \
   --target /path/to/audio/target.wav \
   --source /path/to/audio/source.wav \
   --audio  /path/to/audio/output.wav \
   --play

.. hint:: 
   The ``\`` above is simply to break the command into multiple lines, and make the code snippet more readable.

We can additionally specify different audio parameters, such as grain duration (``grain_dur``), grain envelope (``grain_env``), or the mix between the corpus sources and the original target (``corpus_weights``), like so:

.. code:: shell

   gamut \
   --target /path/to/audio/target.wav \
   --source /path/to/audio/source.wav \
   --audio  /path/to/audio/output.wav \
   --params grain_dur=0.3 grain_env={0,1,0.2,0.1,0} corpus_weights=0.75 \
   --play

.. note:: 
   For a full list of audio parameters that can be used with the ``--params`` argument, click :class:`here<gamut.features.Audio>`.

As you can see, however, :marked:`this workflow can quickly become cumbersome and messy, which is why GAMuT allows to do audio musaicking through JSON scripts.` This is explained :doc:`next <workspace>`.