## **GAMuT: Granular Audio Musaicing Toolkit**

---
![](https://static.wixstatic.com/media/98a1eb_4dbc341ffab04996a39617bf4e6117bf~mv2.png/v1/fill/w_856,h_534,al_c,q_90,usm_0.66_1.00_0.01/logo.webp)

### **Description**

**GAMuT** is a high-level, user-friendly [_granular audio musaicing toolkit_](https://www.francoispachet.fr/musaicing/) implemented in Python. Here are some examples of audio musaicing made with **GAMuT**:
- Target file: [Ángel Gonzalez's "muerte en el olvido" excerpt](https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/00+target_AG-muerte_en_el_olvido.mp3)
- Output: [Female singer corpus](https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/01+Female_corpus+-+1221+files.mp3)
- Output: [CMaj7 chord corpus](https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/02+CMaj_corpus+-+340+files.mp3)
- Output: [String instruments corpus](https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/03+String_corpus+-+1234+files.mp3)
- Output: [Tam tam corpus](https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/04+Tamtam_corpus+-+2878+files.mp3)
- Output: [Woodwind instruments corpus](https://d2cqospqxtt8fw.cloudfront.net/personal-website/media/audio/05+Wind_corpus+-+412+files.mp3)
  

---

### **Installation**

To install `gamut`, simply run the `pip install gamut` command in the terminal.

---

### **Documentation**

Broadly speaking, the audio musaicing pipeline with **GAMuT** is the following:
1. build a **corpus** from one or more sound files.
2. get an audio musaicing **recipe** from the **corpus**, given a **target** sound file.
3. cook the audio musaicing **recipe** and write it into **sound file**.

To do this, a small collection of functions are included:

#### **Main functions**

- `build_corpus()`: Takes a folder directory, or an audio file directory, or a list of directories to audio files, and returns a `dict` object (i.e. the _corpus_). The output can be saved as a `.gamut` file with the `dict_to_gamut()` function, for later use in `get_audio_recipe()`.
  - **Required arguments**:
    -  `input_dir` (`str` or `list`): Input audio file/folder directory, or list of audio file directories, from which to build a corpus.
  - **Optional arguments**:      
    -  `max_duration` (`int`): maximum duration to analyze for all sound files in `input_dir`. If set to `None`, all sound files are analyzed in full. (_Default: None_)
    -  `n_mfcc` (`int`): number of MFCC bands. (_Default: 13_)
    -  `hop_length` (`int`): gap between subsequent frames, in samples. (_Default: 512_)
    -  `frame_length` (`int`): size of analysis window, in samples. (_Default: 1024_)
    -  `kd` (`int`): maximum number of MFCC bands to use for data query tree. If set to `None`, a number is internally chosen based on the number of data samples.(_Default: None_)
   - **Returns** (`dict`): corpus dictionary object.

- `get_audio_recipe()`: Takes an audio sample directory/path (i.e. the _target_) and a `dict` object (i.e. the _corpus_), and returns another `dict` object containing the instructions to rebuild the _target_ using grains from the _corpus_. The output can be saved as a `.gamut` file with the `dict_to_gamut()` function, for later use in `cook_recipe()`.
  - **Required arguments**:      
    - `target_dir` (`str`): directory of target sound file.
    - `corpus_dict` (`dict`): dictionary object containing corpus.
  - **Optional arguments**:
    - `max_duration` (`int`): maximum duration to analyze for target sound file. If set to `None`, the sound file is analyzed in full.(_Default: None_)
    - `hop_length` (`int`): gap between subsequent frames, in samples. (_Default: 512_)
    - `frame_length`(`int`): size of analysis window, in samples. (_Default: 1024_)
    - `kn`: number of best matches (KNN) to include in recipe. (_Default: 8_)
  - **Returns** (`dict`): target recipe dictionary object. 

- `cook_recipe()`: Takes a `dict` object (i.e. the _recipe_), and returns an array of audio samples, intended to be written as an audio file.
  - **Required arguments**:      
    - `recipe_dict` (`dict`): directory object containing audio recipe.
  - **Optional arguments**:      
    - `grain_dur` (`int`, `float` or `list`): fixed value or envelope break points for grain duration, in seconds. (_Default: 0.1_)
    - `stretch_factor` (`int`, `float` or `list`): fixed value or envelope break points for strech factor (i.e. speed).  (_Default: 1_)
    - `onset_var` (`int`, `float` or `list`): fixed value or envelope break points for grain onset variation, in seconds. (_Default: 0_)
    - `target_mix` (`int`, `float` or `list`)*: fixed value or envelope break points for wet/dry mix, in the range of 0.0 to 1.0. (_Default: 0_)
    - `pan_depth` (`int`, `float` or `list`): fixed value or envelope break points for panning depth (>= 0). (_Default: 5_)
    - `kn` (`int`): maximum number of best matches to choose from for each grain. (_Default: 8_)
    - `n_chans` (`int`): number of output channels. (_Default: 2_)
    - `envelope` (`str` or `list`): list of envelope break points, or string specifying [window types](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.get_window.html#scipy.signal.get_window). (_Default: 'hann'_)
    - `sr` (`int`): sampling rate of output. If set to `None`, the target's sampling rate is used. (_Default: None_)    
    - `frame_length_res` (`int`): window size quantization unit. Larger windows increase efficiency at the expense of resolution in grain duration. (_Default: 512_)
  - **Returns** (`ndarray`): numpy array of audio samples.

Additionally, the following functions are included to read and write audio and `.gamut`[1] files:

- `dict_to_gamut()`: writes `dict` object into a `.gamut` file. This function is a simple wrapper of `numpy.save()`.
  - **Required arguments**:
    - `dict` (`dict`): dictionary containing corpus or recipe data.
    - `output_dir` (`str`): output directory for `.gamut` file.
  - **Returns** (`NoneType`): None
- `dict_from_gamut()`: reads a `.gamut` file as a `dict` object. This function is a simple wrapper of `numpy.load()`.
  - **Required arguments**:      
    - `input_dir` (`str`): input directory for `.gamut` file. 
  - **Returns** (`dict`): dictionary containing corpus or recipe data.
- `write_audio()`: writes an `ndarray` as audio. This function is a simple wrapper of `soundfile.write()`.
  - **Required arguments**:      
    - `output_dir` (`str`): output directory of audio file. Output file format must be `.wav`, `.aif`, or `.aiff`.
    - `ndarray` (`ndarray`): numpy array containing audio samples.
  - **Optional arguments**:      
    - `sr` (`int`): audio sampling rate of output file. (_Default: 44100_)
    - `bit_depth` (`int`): audio bit rate of output file. (_Default: 24_)
  - **Returns** (`NoneType`): None
- `play_audio()`: plays back an `ndarray` as audio. This function is a simple wrapper of `sounddevice.write()`. 
  - **Required arguments**:      
    - `ndarray` (`ndarray`): numpy array containing audio samples.
  - **Optional arguments**:      
    - `sr` (`int`): audio sampling rate. (_Default: 44100_)
  - **Returns** (`NoneType`): None 

[1]: `.gamut` is a custom binary data format used for storing **GAMuT** corpora and recipe data. This file is simply a renaming of Numpy's `.npy` file extension.

---

### **Examples**

- **Basic**: generates _corpus_, _recipe_, and _audio_ in a single script — _very slow, not recommended_.
```python
# imports
from gamut import gamut

# set target sound
target = './my_soundfile.wav'

# set corpus folder containing audio samples
audio_files = './my_audio_folder/'

 # build corpus
corpus = gamut.build_corpus(input_dur=audio_files)

 # make target recipe
recipe = gamut.get_audio_recipe(target_dir=target, corpus_dict=corpus)

# cook target recipe
audio_array = gamut.cook_recipe(recipe_dict=recipe)

# write output into audio file
gamut.write_audio(output_dir='./output.wav', ndarray=audio_array)

# plays back audio file
gamut.play_audio(ndarray=audio_array)
```

- **Build corpus**: Builds and writes `.gamut` corpus into file for future reuse.

```python
# imports
from gamut import gamut

# set directory to audio folder
audio_files = './my_audio_folder/'

# build corpus from folder
my_corpus = gamut.build_corpus(input_dir=audio_files)

# set corpus output dir
output_dir = './my_corpus.gamut'

# write corpus into disk
gamut.dict_to_gamut(dict=my_corpus, output_dir=output_dir)
```

- **Make recipe**: Makes and writes `.gamut` recipe into file for future reuse.

```python
# imports
from gamut import gamut

# directory of audio target
target_dir = './my_target_sound.wav'

# gamut corpus dir
corpus_dir = './my_corpus.gamut'

# load corpus
corpus = gamut.dict_from_gamut(input_dir=corpus_dir)

# build audio recipe
target_recipe = gamut.get_audio_recipe(target_dir=target_dir, corpus_dict=corpus)

# set recipe output dir
output_dir = './my_recipe.gamut'

# write recipe into disk
gamut.dict_to_gamut(dict=target_recipe, output_dir=output_dir)
```

- **Cook recipe**: Generates and writes audio file (`.wav`, `.aif`. or `.aif`) from `.gamut` recipe.

```python
# imports
from gamut import gamut

# audio recipe dir
recipe_dir = './my_recipe.gamut'

# load corpus
recipe = gamut.dict_from_gamut(input_dir=recipe_dir)

# cooking settings
envelope = [0, 1, 0.5, 0.1, 0] # grain amplitude envelope (type: str, int, float or list -- if str, use scipy.signal.windows types)
grain_dur = [0.05, 0.25] # grain duration (type: int, float, or list)
sr = 44100 # output sampling rate (type: int)
pan_depth = [1, 40] # depth of panning across channels (>= 0) (type: int, float or list)
target_mix = [0, 0.5] # dry/wet mix of input target (0.0-1.0) (type: int, float, or list)

# cook audio recipe
audio_array = gamut.cook_recipe(recipe_dict=recipe,
                        grain_dur=grain_dur,
                        target_mix=target_mix,
                        pan_depth=pan_depth,
                        envelope=envelope,
                        sr=sr)

# set audio output dir
output_dir = './output.wav'

# write audio into disk
gamut.write_audio(output_dir=output_dir,
            ndarray=audio_array,
            sr=sr,
            bit_depth=24)

# plays back audio file
gamut.play_audio(ndarray=audio_array)            
```

---

### **License**

ISC License
Copyright (c) 2022, [Felipe Tovar-Henao](https://www.felipe-tovar-henao.com/)

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.