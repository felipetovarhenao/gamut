#   ----------------------------------------------------------------------
#   ------------------ MAKE AUDIO MOSAICING RECIPE ------------------------
#   ---------------------------------------------------------------------- 

# PATHS
target = '/Users/felipe-tovar-henao/Documents/Camus files/target_samples/Je respire ou tu palpites.wav'
corpus_path = '/Users/felipe-tovar-henao/Documents/Camus files/corpora/PluckedStrings_corpus.camus'
recipe_dir = '/Users/felipe-tovar-henao/Documents/Camus files/recipes/'

# RECIPE SETTINGS
hop_length = 256
frame_length = 1024
duration = None
k = 8

# ------------------ MAIN ------------------------
# MODULES
from camus import get_audio_recipe, dict_from_camus, dict_to_camus
from os.path import basename, splitext, exists, join
from os import mkdir
import time

st = time.time()

corpus = dict_from_camus(corpus_path)
# MAKE RECIPE
recipe = get_audio_recipe(target, corpus, 
                            hop_length=hop_length, 
                            frame_length=frame_length, 
                            duration=duration,
                            k=k)

# WRITE RECIPE
recipe_name = splitext(basename(target))[0] + '_from_' + splitext(basename(corpus_path))[0]
if not exists(recipe_dir):
    mkdir(recipe_dir)
outpath = join(recipe_dir, recipe_name)
print('...saving recipe {}...'.format(recipe_name))
dict_to_camus(recipe, outpath=outpath)
end = time.time()
print('\nDONE writing {}\nElapsed time: {} seconds'.format(recipe_name, round(end-st, 2)))