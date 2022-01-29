#   ----------------------------------------------------------------------
#   ------------------ MAKE AUDIO MOSAICING RECIPE -----------------------
#   ----------------------------------------------------------------------

# imports 
from gamut import gamut

# path of audio target
target_path = '/Users/felipe-tovar-henao/Documents/GAMuT files/target_samples/poeme_verlaine_48kHz.wav'

# gamut corpus path
corpus_path = '/Users/felipe-tovar-henao/Documents/GAMuT files/corpora/PreparedPiano_corpus.gamut'

# load corpus
corpus = gamut.dict_from_gamut(corpus_path)

# build audio recipe
target_recipe = gamut.get_audio_recipe(target_dir=target_path, corpus_dict=corpus)

# set recipe output path
outfile_path = '/Users/felipe-tovar-henao/Documents/GAMuT files/recipes/poeme_PreparedPiano.gamut'

# write recipe into disk
gamut.dict_to_gamut(dict=target_recipe, output_dir=outfile_path)



