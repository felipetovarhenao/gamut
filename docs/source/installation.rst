Installation
==================

To install, simply run ``pip install gamut`` in the terminal.

.. warning::
	Unfortuntately, as of Feb 3, 2023, **GAMuT** does not work with Python 3.11.
	Make sure your Python version is `v3.10.9 <https://www.python.org/downloads/release/python-3109/>`_ or older.

Other dependencies
------------------

You might also need to install the ``libsndfile1`` and/or ``ffmpeg`` libraries.

* On Mac, run ``brew install libsndfile1 ffmpeg`` (assuming you already have `brew` installed).
* On Debian-based Linux, run ``apt-get update && apt-get install -y libsndfile1 ffmpeg``.

.. note::
	This package was developed, and has only been tested on MacOS. If you're able to use it in another
	operating system and would like to share the installation process, please submit a ``pull request``
	to the `GAMuT github repo <https://github.com/felipetovarhenao/gamut>`_.