#   ------------------------------------------------------------------
#   ------------------ COOK AUDIO FROM RECIPE ------------------------
#   ------------------------------------------------------------------

# imports 
from camus import camus

# audio recipe path
recipe_path = '/Users/felipe-tovar-henao/Desktop/MyRecipe.camus'

# load corpus
recipe = camus.dict_from_camus(recipe_path)

# cooking settings
envelope = [0, 1, 0.5, 0.1, 0] # grain amplitude envelope (type: str, int, float or list -- if str, use scipy.signal.windows types) 
grain_dur = [0.05, 0.25] # grain duration (type: int, float, or list)
sr = 44100 # output sampling rate (type: int)
pan_width = [0.1, 0.9] # spread of stereo image (0.0-1.0) (type: int, float or list)
target_mix = [0, 0.5] # dry/wet mix of input target (0.0-1.0) (type: int, float, or list)

# cook audio recipe
audio_array = camus.cook_recipe(recipe_dict=recipe,
                        envelope=envelope,
                        grain_dur=grain_dur,
                        sr=sr,
                        pan_width=pan_width,
                        target_mix=target_mix)

# set audio output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyAudioMosaicing.wav'

# write audio into disk
camus.write_audio(path=outfile_path, 
            ndarray=audio_array, 
            sr=sr, 
            bit_depth=24)


