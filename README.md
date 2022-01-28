## **GAMuT: Granular Audio Musaicing Toolkit**

---

### **Description**

GAMuT is a high-level, user-friendly _[granular audio musaicing](https://www.francoispachet.fr/musaicing/) toolkit_ implemented in Python.

---

### Installation

To install `gamut`, run the `pip install gamut` command in the terminal.

---

#### **Main functions**

- `build_corpus()`: Takes a folder directory, or an audio file directory, or a list of directories to audio files, and returns a `dict` object (i.e. the _corpus_). The output can be saved as a `.gamut` file with the `dict_to_gamut()` function, for later use in `get_audio_recipe()`.
  - **Arguments**:
    -  `input_dir` (`str` or `list`): Input audio file/folder directory, or list of audio file directories, from which to build a corpus.
    -  `max_duration` (`int`): maximum duration to analyze for all samples in `input_dir`. (_Default: None_)
    -  `n_mfcc` (`int`): number of MFCC bands. (_Default: 13_)
    -  `hop_length` (`int`): gap between subsequent frames, in samples. (_Default: 512_)
    -  `frame_length` (`int`): size of analysis window, in samples. (_Default: 1024_)
    -  `kd` (`int`): maximum number of bands to use for data query tree. (_Default: None_)
   - **Returns** (`dict`): corpus dictionary object.

- `get_audio_recipe()`: Takes an audio sample directory/path (i.e. the _target_) and a `dict` object (i.e. the _corpus_), and returns another `dict` object containing the instructions to rebuild the _target_ using grains from the _corpus_. The output can be saved as a `.gamut` file with the `dict_to_gamut()` function, for later use in `cook_recipe()`.
  - **Arguments**:
    - `target_path` (`str`): directory of target sound file.
    - `corpus_dict` (`dict`): dictionary object containing corpus.
    - `max_duration` (`int`): maximum duration to analyze for target sound file. (_Default: None_)
    - `hop_length` (`int`): gap between subsequent frames, in samples. (_Default: 512_)
    - `frame_length`(`int`): size of analysis window, in samples. (_Default: 1024_)
    - `kn`: number of best matches (KNN) to include in recipe. (_Default: 8_)
  - **Returns** (`dict`): target recipe dictionary object. 

- `cook_recipe()`: Takes a `dict` object (i.e. the _recipe_), and returns an array of audio samples, intended to be written as an audio file.
  - **Arguments**:
    - `recipe_dict` (`dict`): directory object containing audio recipe.
    - `grain_dur` (`int`, `float` or `list`): fixed value or envelope break points for grain duration, in seconds. (_Default: 0.1_)
    - `stretch_factor` (`int`, `float` or `list`): fixed value or envelope break points for strech factor, in seconds.  (_Default: 1_)
    - `onset_var` (`int`, `float` or `list`): fixed value or envelope break points for grain onset variation, in seconds. (_Default: 0_)
    - `target_mix` (`int`, `float` or `list`)*: fixed value or envelope break points for wet/dry mix, in the range of 0.0 to 1.0. (_Default: 0_)
    - `pan_width` (`int`, `float` or `list`): fixed value or envelope break points for panning width, in the range of 0.0 to 1.0. (_Default: 0.5_)
    - `kn` (`int`): maximum number of best matches to choose from for each grain. (_Default: 8_)
    - `n_chans` (`int`): number of output channels. (_Default: 2_)
    - `envelope` (`str` or `list`): list of envelope break points, or string specifying [window types](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window). (_Default: 'hann'_)
    - `sr` (`int`): sampling rate of output. (_Default: None_)    - `frame_length_res` (`int`): window size quantization unit. Larger windows increase efficiency at the expense of resolution in grain duration. (_Default: 512_)
  - **Returns** (`ndarray`): numpy array of audio samples.

Additionally, the following functions are included to read and write audio and `.gamut`[1] files:

- `dict_to_gamut()`: writes `dict` object into a `.gamut` file. This function is a simple wrapper of `np.save()`.
  - **Arguments**:
    - `dict` (`dict`): dictionary containing corpus or recipe data.
    - `output_dir` (`str`): output directory for `.gamut` file.
  - **Returns** (`void`)
- `dict_from_gamut()`: reads a `.gamut` file as a `dict` object. This function is a simple wrapper of `np.load()`.
  - **Arguments**:
    - `output_dir` (`str`): input directory for `.gamut` file. 
  - **Returns** (`dict`): dictionary containing corpus or recipe data.
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
                        grain_dur=grain_dur,
                        target_mix=target_mix,
                        pan_width=pan_width,
                        envelope=envelope,
                        sr=sr)

# set audio output path
outfile_path = '/Users/felipe-tovar-henao/Desktop/MyAudioMosaicing.wav'

# write audio into disk
gamut.write_audio(path=outfile_path,
            ndarray=audio_array,
            sr=sr,
            bit_depth=24)
```
