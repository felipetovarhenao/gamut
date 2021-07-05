#   ----------------------------------------------------------------------
#   ------------------ MAKE AUDIO MOSAICING RECIPE -----------------------
#   ----------------------------------------------------------------------

# imports 
from ..camus import dict_from_camus, get_audio_recipe, dict_to_camus

# path of audio target
target_path = './MyAudioTarget.wav'

# camus corpus path
corpus_path = './MyCorpus.camus'

# load corpus
corpus = dict_from_camus(corpus_path)

# build audio recipe
target_recipe = get_audio_recipe(target_path=target_path, corpus_dict=corpus)

# set recipe output path
outfile_path = './MyRecipe'

# write recipe into disk
dict_to_camus(dict=target_recipe, outpath=outfile_path)



