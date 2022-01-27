#   ----------------------------------------------------------------------
#   ------------------------- GENERAL EXAMPLE ----------------------------
#   ---------------------------------------------------------------------- 

# imports
from gamut import gamut

# set target sound
target = './soundfile.wav'

# set corpus folder containing audio samples
audio_files = './audio_folder'

 # build corpus
corpus = gamut.build_corpus(audio_files)

 # make target recipe
recipe = gamut.get_audio_recipe(target, corpus)

# cook target recipe
output = gamut.cook_recipe(recipe)

# write output into audio file
gamut.write_audio('./output.wav',output)