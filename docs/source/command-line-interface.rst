Command-line interface
======================

**GAMuT** (`v1.0.6` or older) comes with a simple but convenient command-line interface utility, which can be especially helpful if you're brand new to Python, or even programming.

Quickstart
--------------

Once :doc:`installed <./installation>`, we can check the **GAMuT** package version and test it, by running:

.. code:: shell

   gamut --version
   gamut --test

If you see a success message afterwards, it means we're all set.


GAMuT workspace
~~~~~~~~~~~~~~~~~
The quickest way to start with **GAMuT** is by creating a workspace folder. Navigate to where you would want your workplace folder to be, and run:

.. code:: shell

   gamut --start "my-gamut-workspace"

You may choose to name your workspace folder as you wish. In this case, folder named `my-gamut-workspace` will automatically be created for you, and will contain some boilerplate files to help you get started.
We can go into the directory and the current folder structure:

.. code:: shell

   cd ./my-gamut-workspace
   ls

The workspace should look something like this:

.. code::

   my-gamut-workspace
      ├── audio
      │   ├── input
      │   │   ├── source.wav
      │   │   └── target.wav
      │   └── output
      ├── gamut
      │   ├── corpora
      │   └── mosaics
      ├── scripts          
      │   └── test.json
      └── parser.py
   
As you can see, it includes 4 different files:

* ``parser.py``: a Python script that does most of the heavy-lifting. You do **not** need to ever open it or modify its contents. As long as it's there, everything should run smoothly.
* ``audio/input/source.wav`` and ``audio/input/target.wav``: Two default audio samples that we can use to test **GAMuT**.
* ``scripts/test.json``: A JSON file containing boiler-plate information we can use to generate an audio mosaic. This is what we'll be feeding **GAMuT** to create new sounds.

We can now create our first audio mosaic. Let's run the ``test.json`` script:

.. code:: shell

   gamut --script ./scripts/test.json --play

Let's understand what this does:

* ``--script`` specifies we want ``gamut`` to run a script. We can optionally type ``-s`` instead of ``--script`` to make it shorter.
* ``./scripts/test.json`` is the location of the script we want to run. We'll take a loot at this file soon and understand its main components.
* ``--play`` tells ``gamut`` to play the resulting audio at the end of the process. If absent, it won't play it automatically, but the file will still be created.

After running this, we should find a newly created files:

* ``./gamut/corpora/test-corpus.gamut``: A binary file that represents a **corpus** built from ``source.wav``,
* ``./gamut/mosaics/test-mosaic.gamut``: A binary file that represents a **mosaic** built from the audio target ``target.wav``, and the corpus ``test-corpus.gamut``.
* ``./audio/output/test-audio.wav``: The resulting **audio mosaic** in ``.wav`` format.


Now let's open ``scripts/test.json`` and look what's inside:

.. literalinclude:: ./_static/test.json
   :language: json
   :linenos:
   :emphasize-lines: 5, 13
   :caption: Boiler-plate content in ``scripts/test.json``

This ``JSON`` file consists of **three blocks** that represent the basic `audio musaicing` pipeline in **GAMuT** — it essentially says `create a corpus, then a mosaic, and then an audio file.`
We can think of this file as containing all the different settings that **GAMuT** can use to do its job.

Highlighted, are the **two lines** that you should start to experiment with:

* ``corpus::source``: This line specifies the path to an audio file, folder directory, or list thereof, you want to use as a **corpus**.
* ``mosaic::target``: This line specifies the path to an audio file you want to use as a **target**.

.. hint::
   To avoid re-building corpus and/or audio everytime you run the script, you can use the ``--skip <block>`` argument to skip blocks you don't want to run. For instance, this runs the ``test.json`` script, but only the ``audio`` block:

   .. code:: bash

      gamut -s ./scripts/test.json --skip corpus mosaic

Inside each block, you have other parameter fields that you can change. Aside from ``name``, which specifies the name of the output file, you can learn about what each of these parameters mean through these links:

* :class:`corpus block parameters <gamut.features.Corpus>`
* :class:`mosaic block parameters <gamut.features.Mosaic>`
* :class:`audio block parameters <gamut.features.Audio>`

.. note::
   Once you feel more comfortable working with the **GAMuT** `command-line interface`, you may want to go through the :doc:`Python tutorials <getting-started>` to have more control over your workflow.
