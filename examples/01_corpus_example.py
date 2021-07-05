#   ----------------------------------------------------------------------
#   ------------------ BUILD AUDIO MOSAICING CORPUS ----------------------
#   ---------------------------------------------------------------------- 

# imports
from ..camus import build_corpus, dict_to_camus

# set path to audio folder
audio_folder = '/MyAudioFolder'

# build corpus from folder
my_corpus = build_corpus(folder_dir=audio_folder)

# set corpus output path
outfile_path = './MyCorpus'

# write corpus into disk
dict_to_camus(dict=my_corpus, outpath=outfile_path)

