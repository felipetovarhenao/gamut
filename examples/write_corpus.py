from gamut.corpus import Corpus

# -------------------------------
# WRITE A CORPUS TO DISK
# -------------------------------

# 1) create a corpus from one or more audio sources:
# path to directory or audio file(s) to build corpus from (a list of paths is also possible)
source = '/path/to/source/audio/folder-or-file'
corpus = Corpus(source)

# 2) write corpus to disk
# path to output filename (must be a .gamut file format)
output_path = 'path/to/my_corpus.gamut'
corpus.write(corpus)
