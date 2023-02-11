Option 2: GAMuT workspace (recommended)
=========================================

A more convenient way to start working with **GAMuT** is by creating a workspace folder. Navigate to where you would want your workplace folder to be, and run:

.. code:: shell

   gamut --init my-gamut-workspace

You may choose to name your workspace folder differently, instead of ``my-gamut-workspace``. In this case, a folder named `my-gamut-workspace` will automatically be created, and will contain some boilerplate files and folders to help you get started.
We can go into the directory and the current folder structure:

.. code:: shell

   cd ./my-gamut-workspace
   ls

The workspace should look something like this:

.. code::

   my-gamut-workspace
      ├── audio
      │   ├── source.wav
      │   └── target.wav
      ├── corpora
      ├── mosaics
      └── scripts          
          └── test.json
   
As you can see, it includes **4 folders** and **3 different files**. These files are:

   * ``source.wav`` and ``target.wav``: Two default audio samples that we can use to test **GAMuT**.
   * ``test.json``: A JSON file containing boiler-plate information we can use to generate an audio mosaic. This is what we'll be modifying and feeding **GAMuT** to create new sounds.

We can now create our first audio mosaic. Let's run the ``test.json`` script:

.. code:: shell

   gamut --script ./scripts/test.json --play

Let's understand what this does:

  * ``--script`` specifies we want ``gamut`` to run a script. We can optionally type ``-s`` instead of ``--script`` to make it shorter.
  * ``./scripts/test.json`` is the location of the script we want to run. We'll take a loot at this file soon and understand its main components.
  * ``--play`` tells ``gamut`` to play the resulting audio at the end of the process. If absent, it won't play it automatically, but the file will still be created.

After running this, we should find a newly created files:

  * ``./corpora/test-corpus.gamut``: A binary file that represents a **corpus** built from ``source.wav``,
  * ``./mosaics/test-mosaic.gamut``: A binary file that represents a **mosaic** built from the audio target ``target.wav``, and the corpus ``test-corpus.gamut``.
  * ``./audio/test-audio.wav``: The resulting **audio mosaic** in ``.wav`` format.


Now let's open ``scripts/test.json`` and look what's inside:

.. literalinclude:: ../_static/test.json
   :language: json
   :linenos:
   :emphasize-lines: 5, 13
   :caption: Boiler-plate content in ``scripts/test.json``

This ``JSON`` file consists of **three blocks** that represent the basic `audio musaicking` pipeline in **GAMuT** — it essentially says `create a corpus, then a mosaic, and then an audio file.`
We can think of this file as containing all the different settings that **GAMuT** can use to do its job.

Highlighted, are the **two lines** that you should start to experiment with:

  * ``corpus::source``: This line specifies the path to an audio file, folder directory, or list thereof, you want to use as a **corpus**.
  * ``mosaic::target``: This line specifies the path to an audio file you want to use as a **target**.

.. hint::
   To avoid re-building corpus and/or audio everytime you run the script, you can use the ``--skip <block>`` argument to skip blocks you don't want to run. For instance, this runs the ``test.json`` script, but only the ``audio`` block:

   .. code:: bash

      gamut -s ./scripts/test.json --skip corpus mosaic

.. note::
   Script block names **must start** with either ``corpus``, ``audio``, or ``mosaic``. This makes it possible to include, for instance, more than one corpus in the same script:

   .. code:: javascript

      {
         "corpus_1": {
            ...
         },
         "corpus_2": {
            ...
         }
      }

Inside each block, you have other parameter fields that you can change. Aside from ``name``, which specifies the name of the output file for each block, you can learn about what each of these parameters controls through these links:

   * :class:`corpus<gamut.features.Corpus>`
   * :class:`mosaic<gamut.features.Mosaic>`
   * :class:`audio<gamut.features.Audio>`

.. note::
   Once you feel more comfortable working with the **GAMuT** `command-line interface`, you may want to go through the :doc:`Python tutorials <../getting-started>` to have more control over your workflow.
