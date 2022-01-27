#   ----------------------------------------------------------------------
#   ------------------ BUILD AUDIO MOSAICING CORPUS ----------------------
#   ---------------------------------------------------------------------- 

# imports
from gamut import gamut

# set path to audio folder
audio_folder = '/Users/felipe-tovar-henao/Documents/Sample collections/Violin_notes'

# build corpus from folder
my_corpus = gamut.build_corpus(folder_dir=audio_folder)

# set corpus output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyCorpus'

# write corpus into disk
gamut.dict_to_gamut(dict=my_corpus, outpath=outfile_path)

