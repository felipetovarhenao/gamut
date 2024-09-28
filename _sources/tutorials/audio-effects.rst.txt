Tutorial 9: Audio effects
============================

Although the main focus of **GAMuT** is `audio mosaicking`, it might increasingly include a few simple, but useful ways to
apply audio effects to the resulting audio files.

Currently, **GAMuT** supports `audio convolution <https://www.izotope.com/en/learn/the-basics-of-convolution-in-audio-production.html>`_,
which we can use, among other things, to do `convolution reverb <https://ask.audio/articles/what-is-convolution-reverb>`_ with any 
`impulse response <https://en.wikipedia.org/wiki/Impulse_response>`_ we get our hands on.

Here's a brief example on how this can be done:

.. code:: python

	from gamut import Mosaic

	# read .gamut mosaic file
	mosaic = Mosaic()
	mosaic.read('./my_mosaic.gamut')

	# convert to audio
	audio = mosaic.to_audio()

	# convolve audio with impulse response
	audio.convolve('/path/to/audio/impulse/response.wav')

	# play it
	audio.play()

.. hint::
	There are many freely available impulse response packs and libraries online that you can use.
	Here's one such `website <https://impulses.prasadt.com/>`_, where you can download different IRs and experiment with **GAMuT**.