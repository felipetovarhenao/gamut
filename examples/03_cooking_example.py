#   ------------------------------------------------------------------
#   ------------------ COOK AUDIO FROM RECIPE ------------------------
#   ------------------------------------------------------------------

# imports 
from ..camus import dict_from_camus, cook_recipe, write_audio

# audio recipe path
recipe_path = './MyRecipe.camus'

# load corpus
recipe = dict_from_camus(recipe_path)

# cooking settings
envelope = [0, 1, 0.9, 0.5, 0] # grain amplitude envelope (type: str, int, float or list -- if str, use scipy.signal.windows types) 
grain_dur = 0.25 # grain duration (type: int, float, or list)
sr = 44100 # output sampling rate (type: int)
stereo = [0.1, 0.9] # spread of stereo image (0.0-1.0) (type: int, float or list)
target_mix = [0, 0.5] # dry/wet mix of input target (0.0-1.0) (type: int, float, or list)

# cook audio recipe
audio_array = cook_recipe(recipe_dict=recipe,
                        envelope=envelope,
                        grain_dur=grain_dur,
                        sr=sr,
                        stereo=stereo,
                        target_mix=target_mix)

# set audio output path
outfile_path = './MyAudioMosaicing.wav'

# write audio into disk
write_audio(path=outfile_path, 
            ndarray=audio_array, 
            sr=sr, 
            bit_depth=24)



