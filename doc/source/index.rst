.. GAMuT documentation master file, created by
   sphinx-quickstart on Sun Jan 29 15:08:32 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

GAMuT documentation
=================================

.. image:: https://camo.githubusercontent.com/b05386059ba8661e04f1b7ae846d2bc8515fbbb35a915526ccc1324151edd152/68747470733a2f2f7374617469632e7769787374617469632e636f6d2f6d656469612f3938613165625f34646263333431666661623034393936613339363137626634653631313762667e6d76322e706e672f76312f66696c6c2f775f3835362c685f3533342c616c5f632c715f39302c75736d5f302e36365f312e30305f302e30312f6c6f676f2e77656270

**GAMuT** is a high-level, user-friendly granular audio musaicing toolkit implemented in Python. Here are some examples of audio musaicing made with **GAMuT**, using different corpora on the same target:

* **Input target**: An excerpt of Ángel Gonzalez' `muerte en el olvido` (`audio input <https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/00+target_AG-muerte_en_el_olvido.mp3>`_).

And here are 5 different versions of the target, reconstructed with **GAMuT**, using different corpora:

* **Output 1**: Female singer voice corpus (`audio output <https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3>`_).
* **Output 2**: Cmaj7 chord notes corpus (`audio output <https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3>`_).
* **Output 3**: String instruments corpus (`audio output <https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3>`_).
* **Output 4**: Tam-tam corpus (`audio output <https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3>`_).
* **Output 5**: Woodwinds corpus (`audio output <https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3>`_).

To install gamut, simply run ``pip install gamut`` in the terminal.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Corpus
=============

.. automodule:: gamut.corpus
   :members:
   :inherited-members:

Mosaic
=============
.. automodule:: gamut.mosaic
   :members:
   :inherited-members:
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
