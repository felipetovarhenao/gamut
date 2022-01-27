#   ----------------------------------------------------------------------
#   ------------------ MAKE AUDIO MOSAICING RECIPE -----------------------
#   ----------------------------------------------------------------------

# imports 
from camus import camus

# path of audio target
target_path = '/Users/felipe-tovar-henao/Documents/Camus files/target_samples/alfonso.wav'

# camus corpus path
corpus_path = '/Users/felipe-tovar-henao/Desktop/MyCorpus.camus'

# load corpus
corpus = camus.dict_from_camus(corpus_path)

# build audio recipe
target_recipe = camus.get_audio_recipe(target_path=target_path, corpus_dict=corpus)

# set recipe output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyRecipe'

# write recipe into disk
camus.dict_to_camus(dict=target_recipe, outpath=outfile_path)



