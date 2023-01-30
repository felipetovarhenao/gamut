from gamut.corpus import Corpus
from gamut.mosaic import Mosaic

# -------------------------------
# BASIC PIPELINE FOR CREATING AN 
# AUDIO MOSAIC WITH GAMuT
# -------------------------------

# 1) create a corpus from one or more audio sources:
# path to directory or audio file(s) to build corpus from (a list of paths is also possible)
source = '/path/to/source/audio/folder-or-file'
corpus = Corpus(source)

# 2) create a mosaic for a given an audio target and a corpus:
# path to audio file to use as target for audio musaicing
target = '/path/to/target/audio/file'
mosaic = Mosaic(target=target, corpus=corpus)

# 3) convert mosaic to audio buffer and play it:
audio = mosaic.to_audio()
audio.play()
