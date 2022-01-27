## **GAMuT: Granular Audio Musaicing Toolkit**

---

### **Description**

GAMuT is a high-level, user-friendly _[granular audio musaicing](https://www.francoispachet.fr/musaicing/) toolkit_ implemented in Python.

---

### Installation

To install `gamut`, run the `pip install gamut` command in the terminal.

---

#### **Main functions**

- `build_corpus()`: Takes a folder directory, or an audio file directory, or a list of directories to audio files, and returns a `dict` object (i.e. the _corpus_). The output can be saved as a `.gamut` file with the `write_gamut()` function, for later use in `get_audio_recipe()`.

- `get_audio_recipe()`: Takes an audio sample directory/path (i.e. the _target_) and a `dict` object (i.e. the _corpus_), and returns another `dict` object containing the instructions to rebuild the _target_ using grains from the _corpus_. The output can be saved as a `.gamut` file with the `write_gamut()` function, for later use in `cook_recipe()`.

- `cook_recipe()`: Takes a `dict` object (i.e. the _recipe_), and returns an array of audio samples, intended to be written as an audio file.

Additionally, the following functions are included to read and write audio and `.gamut`[1] files:

- `dict_to_gamut()`: writes `dict` object into a `.gamut` file. This function is a simple wrapper of `np.save()`.
- `dict_from_gamut()`: reads a `.gamut` file as a `dict` object. This function is a simple wrapper of `np.load()`.
- `write_audio()`: writes a `ndarray` as audio. This function is a simple wrapper of `sf.write()`.

[1]: `.gamut` is a custom binary data format used for storing **GAMuT** corpora and recipe data. This file is simply a renaming of Numpy's `.npy` file extension.

---

### Examples

- **Basic**: generates _corpus_, _recipe_, and _audio_ in a single script — _not recommended_.
```python
# imports
from gamut import gamut

# set target sound
target = './soundfile.wav'

# set corpus folder containing audio samples
audio_files = './audio_folder'

 # build corpus
corpus = gamut.build_corpus(audio_files)

 # make target recipe
recipe = gamut.get_audio_recipe(target, corpus)

# cook target recipe
output = gamut.cook_recipe(recipe)

# write output into audio file
gamut.write_audio('./output.wav',output)
```

- **Build corpus**: Builds and writes `.gamut` corpus into file for future reuse.

```python
# imports
from gamut import gamut

# set path to audio folder
audio_folder = '/Users/felipe-tovar-henao/Documents/Sample collections/Violin_notes'

# build corpus from folder
my_corpus = gamut.build_corpus(folder_dir=audio_folder)

# set corpus output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/Violin_notes_corpus'

# write corpus into disk
gamut.dict_to_gamut(dict=my_corpus, outpath=outfile_path)
```

- **Make recipe**: Makes and writes `.gamut` recipe into file for future reuse.

```python
# imports
from gamut import gamut

# path of audio target
target_path = '/Users/felipe-tovar-henao/Documents/target_samples/dialogo_44.1Hz.wav'

# gamut corpus path
corpus_path = '/Users/felipe-tovar-henao/Desktop/Violin_notes_corpus'

# load corpus
corpus = gamut.dict_from_gamut(corpus_path)

# build audio recipe
target_recipe = gamut.get_audio_recipe(target_path=target_path, corpus_dict=corpus)

# set recipe output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyRecipe.gamut'

# write recipe into disk
gamut.dict_to_gamut(dict=target_recipe, outpath=outfile_path)
```

- **Cook recipe**: Generates and writes audio file (`.wav`, `.aif`. or `.aif`) `gamut` from recipe.

```python
# imports
from gamut import gamut

# audio recipe path
recipe_path = '/Users/felipe-tovar-henao/Desktop/MyRecipe.gamut'

# load corpus
recipe = gamut.dict_from_gamut(recipe_path)

# cooking settings
envelope = [0, 1, 0.5, 0.1, 0] # grain amplitude envelope (type: str, int, float or list -- if str, use scipy.signal.windows types)
grain_dur = [0.05, 0.25] # grain duration (type: int, float, or list)
sr = 44100 # output sampling rate (type: int)
pan_width = [0.1, 0.9] # spread of panning across channels (0.0-1.0) (type: int, float or list)
target_mix = [0, 0.5] # dry/wet mix of input target (0.0-1.0) (type: int, float, or list)

# cook audio recipe
audio_array = gamut.cook_recipe(recipe_dict=recipe,
                        envelope=envelope,
                        grain_dur=grain_dur,
                        sr=sr,
                        pan_width=pan_width,
                        target_mix=target_mix)

# set audio output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyAudioMosaicing.wav'

# write audio into disk
gamut.write_audio(path=outfile_path,
            ndarray=audio_array,
            sr=sr,
            bit_depth=24)
```
