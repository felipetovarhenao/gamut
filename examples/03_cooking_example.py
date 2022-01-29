#   ------------------------------------------------------------------
#   ------------------ COOK AUDIO FROM RECIPE ------------------------
#   ------------------------------------------------------------------

# imports 
from gamut import gamut
import sounddevice as sd

# audio recipe path
recipe_path = '/Users/felipe-tovar-henao/Documents/GAMuT files/recipes/poeme_PreparedPiano.gamut'

# load corpus
recipe = gamut.dict_from_gamut(recipe_path)

# cooking settings
envelope = [0, 1, 0.5, 0.1, 0] # grain amplitude envelope (type: str, int, float or list -- if str, use scipy.signal.windows types) 
grain_dur = [0.05, 0.25] # grain duration (type: int, float, or list)
sr = 48000 # output sampling rate (type: int)
pan_width = [0.1, 0.9] # spread of stereo image (0.0-1.0) (type: int, float or list)
target_mix = [0, 0.5] # dry/wet mix of input target (0.0-1.0) (type: int, float, or list)

# cook audio recipe
audio_array = gamut.cook_recipe(recipe_dict=recipe,
                        envelope=envelope,
                        grain_dur=grain_dur,
                        sr=sr,
                        pan_spread=pan_width,
                        target_mix=target_mix,
                        n_chans=4)

sd.play(audio_array, samplerate=sr)
sd.wait()
# # set audio output path
# outfile_path = '/Users/felipe-tovar-henao/Desktop/MyAudioMosaicing.wav'

# # write audio into disk
# gamut.write_audio(path=outfile_path, 
#             ndarray=audio_array, 
#             sr=sr, 
#             bit_depth=24)



