#   ----------------------------------------------------------------------
#   ------------------ BUILD AUDIO MOSAICING CORPUS ----------------------
#   ---------------------------------------------------------------------- 

# imports
from gamut import gamut

# set path to audio folder
audio_folder = '/Users/felipe-tovar-henao/Desktop/OrchideaSOL2020/Keyboards/PreparedPiano'

# build corpus from folder
my_corpus = gamut.build_corpus(input_dir=audio_folder)

# set corpus output path
outfile_path = '/Users/felipe-tovar-henao/Documents/GAMuT files/corpora/PreparedPiano_corpus.gamut'

# write corpus into disk
gamut.dict_to_gamut(dict=my_corpus, output_dir=outfile_path)

