Tutorial 6: Audio feature analysis
=================================================

By default, when creating a ``Corpus``, the feature analysis performed on the audio 
sources is an `MFCC` (Mel Frequency Cepstral Coefficient) analysis.

This is meant to capture the `timbral` characteristics of the audio sources, and 
use that as a criteria for matching each segment from the `target` in a ``Mosaic``, 
with possible segments from the audio sources in a ``Corpus``.

However, we can set which features to use when creating a ``Corpus``. Currently,
the available features are:

* ``"timbre"``: equivalent to an `MFCC` analysis.
* ``"pitch"``: equivalent to a `chroma` analysis.

In short, we can create a ``Corpus`` based on `timbre`, `pitch`, or both. 
The decision on which features to use will greatly depend on the types of targets 
you want to use.

Here's a quick example:

.. code:: python

    from gamut.features import Corpus

    # set audio source(s) for corpus
    source = '/path/to/source/audio/folder-or-file'

    # create corpus based on pitch content
    pitch_based_corpus = Corpus(source=source, features=['pitch'])

    # create corpus based on timbral content
    timbre_based_corpus = Corpus(source=source, features=['timbre'])

    # create corpus based on pitch AND timbral content
    pitch_timbre_based_corpus = Corpus(source=source, features=['pitch', 'timbre'])

.. note::
    Specifying which features to use has important implications, since ``Mosaic`` instances are created
    based on the same features used by the input ``Corpus`` instance(s).

    Similarly, when combining ``Corpus`` instances as input for a ``Mosaic``, it will only work if all of them were created 
    on the same features.
