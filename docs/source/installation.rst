Installation
==================

Here's a step-by-step guide on how to install the **GAMuT** package, assumming, of course, that you already have `Python <https://www.python.org/downloads/release/python-3109/>`_ installed.

.. warning::
	As of February of 2023, **GAMuT** is not guaranteed to work with Python 3.11.
	Make sure your Python version is `v3.10.9 <https://www.python.org/downloads/release/python-3109/>`_ or older.

Before installing **GAMuT**, you'll need a few audio and media libraries.

on **MacOS**, run:

	.. code:: shell

		brew install portaudio libsoundio libsndfile ffmpeg

on **Linux Ubuntu**:
	.. code:: shell

		apt-get update -y
		apt-get install -y libportaudio2 libasound-dev libsndfile1 ffmpeg

.. note::
	If you're a Windows user, please Google how to install these libraries in your machine.


Once these libraries are installed, simply run:

	.. code:: shell

		pip install gamut

.. note::
	This package was developed, and has only been tested on **MacOS**. If you're able to use it in another
	operating system and would like to share the installation process, please submit a ``pull request``
	to the `GAMuT github repo <https://github.com/felipetovarhenao/gamut>`_.