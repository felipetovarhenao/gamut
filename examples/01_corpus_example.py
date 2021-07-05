#   ----------------------------------------------------------------------
#   ------------------ BUILD AUDIO MOSAICING CORPUS ----------------------
#   ---------------------------------------------------------------------- 

# import modules
from ..camus import build_corpus, dict_to_camus

# set path to audio folder
audio_folder = '/'

# build corpus from folder
my_corpus = build_corpus(folder_dir=audio_folder)

# set corpus output path
output_path = './'

# write corpus into disk
dict_to_camus(my_corpus, output_path)

