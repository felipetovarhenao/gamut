Installation
==================

Here's a step-by-step guide on how to install the **GAMuT** package, assumming, of course, that you already have `Python <https://www.python.org/downloads/release/python-3109/>`_ installed.

.. warning::
	**GAMuT** is currently guaranteed to work on `Python 3.7.0 <https://www.python.org/downloads/release/python-370>`_ through `Python 3.10.10 <https://www.python.org/downloads/release/python-31010/>`_ (`recommended`). 
	In the near future, it should be compatible with `Python 3.11 <https://www.python.org/downloads/release/python-3112>`_ releases.

Dependencies
--------------

For **GAMuT** to work, you'll need to install `ffmpeg <https://ffmpeg.org/>`_ and at least one of the following audio libraries (listed in order of preference):

	* `libsndfile <https://libsndfile.github.io/libsndfile/>`_
	* `libsoundio <http://libsound.io/>`_
	* `portaudio <http://www.portaudio.com/>`_

To install them on **MacOS**, run (assuming you already have `Homebrew <https://brew.sh/>`_ installed):

	.. code:: shell

		brew install portaudio libsoundio libsndfile ffmpeg

To install them on **Debian-based Linux**:

	.. code:: shell

		apt-get update -y
		apt-get install -y libportaudio2 libasound-dev libsndfile1 ffmpeg

.. admonition:: Note for Windows users
	:class: warning
	
	Installing these libraries on Windows can be a bit tedious, so please Google how to install them in your machine.
	Also notice that for both the libraries and Python, **you will likely have to manually add the executables to the system PATH**. For a detailed guide
	on this, please read these two sources:
	
	- `How to add Python to PATH variable in Windows <https://www.educative.io/answers/how-to-add-python-to-path-variable-in-windows>`_
	- `How to add executables to your PATH in Windows <https://medium.com/@kevinmarkvi/how-to-add-executables-to-your-path-in-windows-5ffa4ce61a53>`_.



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

If you don't see any errors, it means **GAMuT** runs properly in your machine.