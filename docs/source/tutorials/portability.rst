Tutorial 8: Portability
============================

When writing ``Corpus`` and ``Mosaic`` instances to disk, there are some tradeoffs to consider — namely, **portability**.
By **portability** we mean the ability to share ``.gamut`` files, without having to worry about missing files
or broken file/directory paths — in other words, fully self-contained, transferable ``.gamut`` files.

The tradeoff, however, is that `portable` files will be **significantly larger** in size than `non-portable` files, since `portable` 
files will contain the same data as `non-portable` ones, in addition to all the necessary audio files to use it in the future. 
This can be especially cumbersome and memory-inefficient when many audio files are shared among different ``.gamut`` files. 
Therefore, `portability` should only be used in cases when long-term longevity or transferrability of ``.gamut`` files is absolutely 
necessary.

By default, the ``write()`` method in both ``Corpus`` and ``Mosaic`` instances writes `non-portable` ``.gamut`` files to disk,
but this can be changed by setting the ``portable`` keyword argument to ``True`` or ``False``:

.. code:: python
    
    from gamut.features import Corpus, Mosaic

    # write portable corpus to disk
    corpus = Corpus(source='/path/to/source/audio/folder-or-file.wav')
    corpus.write('./my_corpus.gamut', portable=True)
   
    # write portable mosaic to disk
    mosaic = Mosaic(target='/path/to/target/audio/file.wav', corpus=corpus)
    mosaic.write('./my_mosaic.gamut', portable=True)


.. warning::
    When a `non-portable` ``.gamut`` file is written to disk, the absolute directory paths for all audio files are stored in it. 
    This means that changing the name or location of **any of these files** will render the ``.gamut`` file unusable. Hence the 
    benefit of writing `portable` ``.gamut`` files.

.. note::
    ``Mosaic`` instances have the slight benefit of only keeping track of the audio files used for the mosaic, and not the entire ``Corpus``
    from which it was built. Therefore, they can be much smaller in size.