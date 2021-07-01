#   ----------------------------------------------------------------------
#   ------------------ COOK AUDIO FROM RECIPE ------------------------
#   ---------------------------------------------------------------------- 

# PATHS
recipe_path = '/Users/felipe-tovar-henao/Documents/Camus files/recipes/Je respire ou tu palpites_from_PluckedStrings_corpus.json'
sound_out = '/Users/felipe-tovar-henao/Documents/Camus files/output samples/'

# COOKING SETTINGS
grain_dur = [0.05 , 0.1]
onset_var = 0
stretch_factor = 1
kn = 5
target_mix = [1, 0]
# envelope settings
env_type = 0
sustain = 0.6
env_array = [0, 1, 0.85]
sharpness = 12
stereo = [0, 1]
sr = 44100

# ------------------ MAIN ------------------------
# MODULES
from camus import cook_recipe
import soundfile as sf
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
output = cook_recipe(recipe_path, 
                    envelope=env_types[env_type],
                    grain_dur=grain_dur,
                    stretch_factor=stretch_factor,
                    onset_var=onset_var,
                    kn=kn,
                    target_mix=target_mix,
                    stereo=stereo)

# WRITE SOUND TO WAVE
basename = os.path.splitext(os.path.basename(recipe_path))[0]
filename = '{}_d{}_s{}_j{}_e-{}_k{}.wav'.format(
                basename,
                str(grain_dur),
                str(stretch_factor),
                str(onset_var),
                envtag,
                kn
                )
outdir = sound_out + basename
if not os.path.exists(outdir):
    os.makedirs(outdir)

sf.write(os.path.join(outdir, filename), output, sr, 'PCM_24')
end = time.time()
print('DONE cooking {}.\nElapsed time: {}'.format(filename, round(end-st, 2)))