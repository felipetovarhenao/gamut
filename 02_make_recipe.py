#   ----------------------------------------------------------------------
#   ------------------ MAKE AUDIO MOSAICING RECIPE ------------------------
#   ---------------------------------------------------------------------- 

# PATHS
target = '/Users/felipe-tovar-henao/Documents/Camus files/target_samples/poeme_verlaine.wav'
corpus_path = '/Users/felipe-tovar-henao/Documents/Camus files/corpora/Berklee44v2_corpus.camus'
recipe_dir = '/Users/felipe-tovar-henao/Documents/Camus files/recipes/'

# RECIPE SETTINGS
hop_length = 256
frame_length = 1024
duration = None
k = 8

# ------------------ MAIN ------------------------
# MODULES
from camus import get_audio_recipe, read_dictionary, write_dictionary
from os.path import basename, splitext, exists, join
from os import mkdir
import time

st = time.time()

corpus = read_dictionary(corpus_path)
# MAKE RECIPE
recipe = get_audio_recipe(target, corpus, 
                            hop_length=hop_length, 
                            frame_length=frame_length, 
                            duration=duration,
                            k=k)

# WRITE JSON RECIPE
recipe_name = splitext(basename(target))[0] + '_from_' + splitext(basename(corpus_path))[0]
if not exists(recipe_dir):
    mkdir(recipe_dir)
outpath = join(recipe_dir, recipe_name)
print('...saving recipe {}...'.format(recipe_name))
write_dictionary(recipe, outpath=outpath)
end = time.time()
print('\nDONE writing {}\nElapsed time: {} seconds'.format(recipe_name, round(end-st, 2)))