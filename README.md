## **CAMus Engine**
---
### **Description**

CAMus is a _Corpus-based Audio Musaicing Engine_ implemented in Python.

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
- `librosa`
- `progress`

To install them, use the `pip install` command.