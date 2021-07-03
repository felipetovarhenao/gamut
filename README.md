## **CAMus Engine**

### Description

CAMus is a _corpus-based audio musaicing engine_ implemented in Python.
It consists of three main functions: 
- `build_corpus()`: takes a folder directory (i.e. a path) containing audio samples (`.wav`, `.aif`, or `.aiff`) and returns a dictionary object, intended to be saved as a `JSON` file with the `save_JSON()` function.

- `get_audio_recipe()`: takes a audio sample directory/path (i.e. the _target_) and a `JSON` file directory/path (i.e. the _corpus_), and returns another directory containing the necessary information to rebuild the _target_ using grains from the _corpus_. The recipe is intended to be saved as a `JSON` file with the `save_JSON()` function.

- `cook_sound()`: takes a `JSON` file directory/path (i.e. the _recipe_), and returns an array of audio samples, to be written as an audio file.

### System requirements

The following python libraries are required for CAMus to work:
- `librosa`
- `progress`

To install them, use the `pip install` command.