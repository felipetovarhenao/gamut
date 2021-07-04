#   ----------------------------------------------------------------------
#   ------------------ COOK AUDIO FROM RECIPE ------------------------
#   ---------------------------------------------------------------------- 

# PATHS
recipe_path = '/Users/felipe-tovar-henao/Documents/Camus files/recipes/Je respire ou tu palpites_from_Berklee44v11_corpus.camus'
sound_out = '/Users/felipe-tovar-henao/Documents/Camus files/output samples/'

# COOKING SETTINGS
grain_dur = [0.5, 1.5]
onset_var = 0
stretch_factor = 1
kn = 8
target_mix = [0, 0.33, 1]
# envelope settings
env_type = 0
sustain = 0.1
env_array = [0, 1, 0.85]
sharpness = 20
stereo = 1
sr = 44100

# ------------------ MAIN ------------------------
# MODULES
from camus import cook_recipe, dict_from_camus, write_audio
import os
import time

st = time.time()

# ENVELOPE INFO
for x in range(sharpness):
    env_array.append(sustain)
env_array.append(0)

env_types = [
    env_array,
    'hann',
    'hamming'
]
if type(env_types[env_type]) == list:
    envtag = 'array'
else:
    envtag = env_types[env_type]

# COOK SOUND
recipe_dict = dict_from_camus(recipe_path)
output = cook_recipe(recipe_dict=recipe_dict, 
                    envelope=env_types[env_type],
                    grain_dur=grain_dur,
                    stretch_factor=stretch_factor,
                    onset_var=onset_var,
                    kn=kn,
                    target_mix=target_mix,
                    stereo=stereo,
                    sr=sr)

# WRITE SOUND TO WAVE
basename = os.path.splitext(os.path.basename(recipe_path))[0]
filename = '{}_d{}_m{}_s{}_j{}_e-{}_k{}.wav'.format(
                basename,
                str(target_mix),
                str(grain_dur),
                str(stretch_factor),
                str(onset_var),
                envtag,
                kn
                )
outdir = sound_out + basename
if not os.path.exists(outdir):
    os.makedirs(outdir)

write_audio(path=os.path.join(outdir, filename), 
            ndarray=output, 
            sr=sr, 
            bit_depth=24)
end = time.time()
print('DONE cooking {}.\nElapsed time: {}'.format(filename, round(end-st, 2)))