Installation
==================

Here's a step-by-step guide on how to install the **GAMuT** package, assumming, of course, that you already have `Python <https://www.python.org/downloads/release/python-3109/>`_ installed.

.. warning::
	**GAMuT** is currently guaranteed to work on `Python 3.7.0 <https://www.python.org/downloads/release/python-370>`_ through `Python 3.10.9 <https://www.python.org/downloads/release/python-3109/>`_ (`recommended`). 
	In the near future, it should be compatible with `Python 3.11 <https://www.python.org/downloads/release/python-3112>`_ releases.

Dependencies
--------------

Before installing **GAMuT**, you'll need a few system-wide audio and media libraries:

	* `portaudio <http://www.portaudio.com/>`_
	* `libsoundio <http://libsound.io/>`_
	* `libsndfile <https://libsndfile.github.io/libsndfile/>`_
	* `ffmpeg <https://ffmpeg.org/>`_

To install on **MacOS**, run (assuming you already have `Homebrew <https://brew.sh/>`_ installed):

	.. code:: shell

		brew install portaudio libsoundio libsndfile ffmpeg

To install on **Debian-based Linux**:

	.. code:: shell

		apt-get update -y
		apt-get install -y libportaudio2 libasound-dev libsndfile1 ffmpeg

.. note::
	If you're a Windows user, please Google how to install these libraries in your machine.


Python package
---------------

Once these libraries are installed, simply run:

	.. code:: shell

		pip install gamut

.. note::
	This package was developed, and has only been tested on **MacOS**. If you're able to use it in another
	operating system and would like to share the installation process, please submit a ``pull request``
	to the `GAMuT github repo <https://github.com/felipetovarhenao/gamut>`_.


Test
-----------

Once **GAMuT** is installed, you can test that everything works, by running:

	.. code:: shell

		gamut --version
		gamut --test

If you see a success message afterwards, it means **GAMuT** can run in your machine.