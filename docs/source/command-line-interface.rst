.. role:: marked
    :class: marked

Command-line interface
======================

**GAMuT** (`v1.0.6` or older) comes with a simple but convenient command-line interface (CLI) utility, which can be especially helpful if you're brand new to Python, or even programming.

Quickstart
--------------

Once :doc:`installed <./installation>`, we can check the **GAMuT** package version and test it, by running:

.. code:: shell

   gamut --version
   gamut --test

If you see a success message afterwards, it means we're all set.

Option 1: Direct input arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The quickest, but perhaps **least efficient** way of doing audio musaicing with **GAMuT**'s command-line interface is by using `direct input arguments`. For instance:

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
   Although all possible parameters for the ``--params`` argument are explained in more detail throughout the Python :doc:`tutorials </getting-started>`, you can read more about them :class:`here<gamut.features.Audio>`.

:marked:`As you can see, however, this workflow can quickly become cumbersome and messy, which is why GAMuT allows to do audio musaicing through JSON scripts.` This is explained next.

Option 2: GAMuT workspace (recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Inside each block, you have other parameter fields that you can change. Aside from ``name``, which specifies the name of the output file for each block, you can learn about what each of these parameters controls through these links:

   * :class:`corpus<gamut.features.Corpus>`
   * :class:`mosaic<gamut.features.Mosaic>`
   * :class:`audio<gamut.features.Audio>`

.. note::
   Once you feel more comfortable working with the **GAMuT** `command-line interface`, you may want to go through the :doc:`Python tutorials <getting-started>` to have more control over your workflow.
