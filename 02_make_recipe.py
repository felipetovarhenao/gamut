#   ----------------------------------------------------------------------
#   ------------------ MAKE AUDIO MOSAICING RECIPE ------------------------
#   ---------------------------------------------------------------------- 

# PATHS
target = '/Users/felipe-tovar-henao/Documents/Camus files/target_samples/Je respire ou tu palpites.wav'
corpus = '/Users/felipe-tovar-henao/Documents/Camus files/corpora/Winds_corpus.json'
recipe_dir = '/Users/felipe-tovar-henao/Documents/Camus files/recipes/'

# RECIPE SETTINGS
hop_length = 256
frame_length = 1024
duration = None
k = 8

# ------------------ MAIN ------------------------
# MODULES
from camus import get_audio_recipe, save_JSON
from os.path import basename, splitext, exists, join
from os import mkdir
import time

st = time.time()
# MAKE RECIPE
recipe = get_audio_recipe(target, corpus, 
                            hop_length=hop_length, 
                            frame_length=frame_length, 
                            duration=duration,
                            k=k)

### WRITE JSON RECIPE
recipe_name = splitext(basename(target))[0] + '_from_' + basename(corpus)
if not exists(recipe_dir):
    mkdir(recipe_dir)
output = join(recipe_dir, recipe_name)
save_JSON(recipe, output)
end = time.time()
print('DONE writing {}.\nElapsed time: {}'.format(recipe_name, round(end-st, 2)))