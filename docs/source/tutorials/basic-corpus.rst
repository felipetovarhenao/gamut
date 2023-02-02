Tutorial 2: Creating an audio corpus
=================================================

A ``Corpus`` represents a collection of audio `sources` that can be used to re-construct a given audio `target`. 
There are different ways in which we can specify the audio source(s):

* A path to a ``.wav`` or ``.aif`` audio file, as a ``str``.
* A path to a **folder** containing audio files, as a ``str``.
* A ``list`` of paths to folders and/or audio files.

.. note::
	When specifying a folder, **GAMuT** will recursively look for any ``.wav`` or ``.aif`` audio files in the directory, ignoring any other files.

Note that creating a ``Corpus`` can easily be the most computationally expensive part when doing `audio musaicing`, especially when 
we're dealing with large amounts of audio files. To make sure we can reuse every `corpus` we build, 
it's best to write it to disk as a ``.gamut`` file.

Here's a simple script showing how to write ``Corpus`` instances as ``.gamut`` files.

.. code:: python

	from gamut.features import Corpus

	# 1) create a corpus from one or more audio sources:
	# path to directory or audio file(s) to build corpus from (a list of paths is also possible)
	source = [
		'/path/to/source/audio/folder-or-file-1',
		...
		'/path/to/source/audio/folder-or-file-N',
	]
	corpus = Corpus(source=source)

	# 2) write corpus to disk as a .gamut file
	corpus.write('path/to/my_corpus.gamut')

.. note::
	``.gamut`` is a custom binary data format used for storing **GAMuT** corpora and recipe data. This file is simply a renaming of Numpy's ``.npy`` file extension.

Next time we want to use this corpus, we simply read it from disk:

.. code:: python

	from gamut.features import Corpus

	corpus = Corpus().read('path/to/my_corpus.gamut')