from gamut.corpus import Corpus
from gamut.mosaic import Mosaic

# -------------------------------
# WRITE A MOSAIC TO DISK
# -------------------------------

# 1) read corpus from a previously created .gamut file
corpus_path = 'path/to/my_corpus.gamut'
corpus = Corpus()
corpus.read(corpus_path)

# 2) create a mosaic for a given an audio target and a corpus:
# path to audio file to use as target for audio musaicing
target = '/path/to/target/audio/file'
mosaic = Mosaic(target=target, corpus=corpus)

# 3) write to disk
# path to output filename (must be a .gamut file format)
output_path = 'path/to/my_mosaic.gamut'
mosaic.write(output_path)
