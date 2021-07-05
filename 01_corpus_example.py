#   ----------------------------------------------------------------------
#   ------------------ BUILD AUDIO MOSAICING CORPUS ----------------------
#   ---------------------------------------------------------------------- 

# imports
from camus import camus

# set path to audio folder
audio_folder = '/Users/felipe-tovar-henao/Documents/Sample collections/Violin_notes'

# build corpus from folder
my_corpus = camus.build_corpus(folder_dir=audio_folder)

# set corpus output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyCorpus'

# write corpus into disk
camus.dict_to_camus(dict=my_corpus, outpath=outfile_path)

