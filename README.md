## **CAMus Engine**

---

### **Description**

CAMus is a _Corpus-based Audio Musaicing_ engine implemented in Python.

---

#### **Main functions**

- `build_corpus()`: Takes a folder directory (i.e. a path) containing audio samples (`.wav`, `.aif`, or `.aiff`) and returns a `dict` object. The output can be saved as a `.camus` file with the `write_camus()` function, for later use in `get_audio_recipe()`.

- `get_audio_recipe()`: Takes an audio sample directory/path (i.e. the _target_) and a `dict` object (i.e. the _corpus_), and returns another `dict` object containing the instructions to rebuild the _target_ using grains from the _corpus_. The output can be saved as a `.camus` file with the `write_camus()` function, for later use in `cook_recipe()`.

- `cook_recipe()`: Takes a `dict` object (i.e. the _recipe_), and returns an array of audio samples, intended to be written as an audio file.

Additionally, the following functions are included to read and write audio and `.camus`[1] files:

- `dict_to_camus()`: writes `dict` object into a `.camus` file. This function is a simple wrapper of `np.save()`.
- `dict_from_camus()`: reads a `.camus` file as a `dict` object. This function is a simple wrapper of `np.load()`.
- `write_audio()`: writes a `ndarray` as audio. This function is a simple wrapper of `sf.write()`.

[1]: `.camus` is a custom binary data format used for storing **CAMus** corpora and recipe data. This file is simply a renaming of Numpy's `.npy` file extension.

---

### System requirements

The following python libraries are required for CAMus to work:

- `librosa (v0.8.1)`
- `progress (v1.5)`
- `scikit-learn (v0.24.2)`
- `scipy (v1.7.0)`

To install them, use the `pip install` command.

### Basic examples

- Building a corpus

```python
# imports
from camus import camus

# set path to audio folder
audio_folder = '/Users/felipe-tovar-henao/Documents/Sample collections/Violin_notes'

# build corpus from folder
my_corpus = camus.build_corpus(folder_dir=audio_folder)

# set corpus output path
outfile_path = '/Users/MyUserName/Desktop/Violin_notes_corpus'

# write corpus into disk
camus.dict_to_camus(dict=my_corpus, outpath=outfile_path)
```

- Making a recipe

```python
#   ----------------------------------------------------------------------
#   ------------------ MAKE AUDIO MOSAICING RECIPE -----------------------
#   ----------------------------------------------------------------------

# imports
from camus import camus

# path of audio target
target_path = '/Users/felipe-tovar-henao/Documents/target_samples/dialogo_44.1Hz.wav'

# camus corpus path
corpus_path = '/Users/MyUserName/Desktop/Violin_notes_corpus'

# load corpus
corpus = camus.dict_from_camus(corpus_path)

# build audio recipe
target_recipe = camus.get_audio_recipe(target_path=target_path, corpus_dict=corpus)

# set recipe output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyRecipe'

# write recipe into disk
camus.dict_to_camus(dict=target_recipe, outpath=outfile_path)
```

- Cooking a recipe

```python
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
stereo = [0.1, 0.9] # spread of stereo image (0.0-1.0) (type: int, float or list)
target_mix = [0, 0.5] # dry/wet mix of input target (0.0-1.0) (type: int, float, or list)

# cook audio recipe
audio_array = camus.cook_recipe(recipe_dict=recipe,
                        envelope=envelope,
                        grain_dur=grain_dur,
                        sr=sr,
                        stereo=stereo,
                        target_mix=target_mix)

# set audio output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyAudioMosaicing.wav'

# write audio into disk
camus.write_audio(path=outfile_path,
            ndarray=audio_array,
            sr=sr,
            bit_depth=24)
```
