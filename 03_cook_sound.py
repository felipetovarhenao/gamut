#   ----------------------------------------------------------------------
#   ------------------ COOK AUDIO FROM RECIPE ------------------------
#   ---------------------------------------------------------------------- 

# PATHS
recipe_path = '/Users/felipe-tovar-henao/Documents/Camus files/recipes/dialogue_fr_from_Orchset_corpus.json'
sound_out = '/Users/felipe-tovar-henao/Documents/Camus files/output samples/'

# COOKING SETTINGS
# frame_length = 512*(2**2)
frame_length = 2048*4
jitter = 128
stretch_factor = 1
kn = 8
# envelope settings
env_type = 0
sustain = 0.1
env_array = [0, 1, 0.85]
sharpness = 15

sr = 44100

# ------------------ MAIN ------------------------
# MODULES
import camus
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
output = camus.cook_recipe(recipe_path, 
                                envelope=env_types[env_type],
                                frame_length=frame_length,
                                stretch_factor=stretch_factor,
                                jitter=jitter,
                                kn=kn)

# WRITE SOUND TO WAVE
basename = os.path.splitext(os.path.basename(recipe_path))[0]
filename = '{}_f{}_s{}_j{}_e-{}_k{}.wav'.format(
                basename,
                str(frame_length),
                str(stretch_factor),
                str(jitter),
                envtag,
                kn
                )
outdir = sound_out + basename
if not os.path.exists(outdir):
    os.makedirs(outdir)

sf.write(os.path.join(outdir, filename), output, sr, 'PCM_24')
end = time.time()
print('DONE cooking {}.\nElapsed time: {}'.format(filename, round(end-st, 2)))