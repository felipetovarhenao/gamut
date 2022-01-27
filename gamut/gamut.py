from distutils.command.build import build
from os.path import realpath, basename, isdir, splitext, join
from os import walk, rename
import librosa
import numpy as np
from math import floor, log, sqrt
from random import choices, random
from scipy.signal import get_window
from sklearn.neighbors import NearestNeighbors
from progress.bar import IncrementalBar
from progress.counter import Counter
from soundfile import write

np.seterr(divide='ignore')

FILE_EXT = '.gamut'
AUDIO_FORMATS = ['.wav', '.aif', '.aiff']

def dict_to_gamut(dict, outpath):
    '''Writes `dict` object into a `.gamut` file. This function is a simple wrapper of `np.save()`.'''
    outpath = splitext(outpath)[0]
    np.save(outpath, dict)
    rename(outpath+'.npy', outpath+FILE_EXT)


def dict_from_gamut(path):
    '''Reads a `.gamut` file as a `dict` object. This function is a simple wrapper of `np.load()`.'''
    ext = basename(path)[-6:]
    if ext == FILE_EXT:
        return np.load(path, allow_pickle=True).item()
    else:
        raise ValueError(
            'Wrong file extension. Provide a path for a {} file'.format(FILE_EXT))


def write_audio(path, ndarray, sr=44100, bit_depth=24):
    """Writes a `ndarray` as audio. This function is a simple wrapper of `sf.write()`."""
    if splitext(path)[1] not in AUDIO_FORMATS:
        raise ValueError('Audio file format must be .wav, .aif, or .aiff')
    write(path, ndarray, sr, 'PCM_{}'.format(bit_depth))


def array_resampling(array, N):
    x_coor1 = np.arange(0, len(array)-1, (len(array)-1)/N)[:N]
    x_coor2 = np.arange(0, len(array))
    return np.interp(x_coor1, x_coor2, array)


def get_features(file_path, duration=None, n_mfcc=13, hop_length=512, frame_length=1024):
    '''Returns a 3-tuple of ndarrays, consisting of:
            - MFCC frames of audio target (ndarray)
            - Audio target meta-data (ndarray) - i.e. [`sample_index`, `rms_amplitude`, `pitch_centroid`]
            - Sampling rate of target (int).'''
    file_path = realpath(file_path)
    y, sr = librosa.load(file_path, duration=duration, sr=None)
    mfcc_frames = librosa.feature.mfcc(y=y,
                                       sr=sr,
                                       n_mfcc=n_mfcc,
                                       n_fft=frame_length,
                                       hop_length=hop_length).T[:-2]
    rms_frames = librosa.feature.rms(y=y,
                                     frame_length=frame_length,
                                     hop_length=hop_length)[0][:-2]
    centroid_frames = np.log2(librosa.feature.spectral_centroid(y=y,
                                                                sr=sr,
                                                                n_fft=frame_length,
                                                                hop_length=hop_length)[0][:-2]/440)*12+69
    centroid_frames[centroid_frames < 0] = 0
    n_frames = len(rms_frames)
    sample_indxs = np.arange(start=0, stop=n_frames *
                             hop_length, step=hop_length)
    metadata = np.array([sample_indxs, rms_frames, centroid_frames]).T

    return mfcc_frames, metadata, sr


def build_corpus(input_dir, max_duration=None, n_mfcc=13, hop_length=512, frame_length=1024, kd=None):
    '''Takes a folder directory, or an audio file directory, or a list of directories to audio files, and returns a `dict` object. The output can be saved as a `.gamut` file with the `write_gamut()` function, for later use in `get_audio_recipe()`.'''
   
    soundfiles = list() 
   
    # check if input_dir is folder or list of paths
    if type(input_dir) is str: 
        input_dir = realpath(input_dir)
        if isdir(input_dir):
            read_mode = 'folder'
        elif splitext(input_dir)[1] in AUDIO_FORMATS:
            read_mode = 'audio file'
            soundfiles.append(input_dir)
        corpus_name = '{}: {}'.format(read_mode, basename(input_dir))
    elif type(input_dir) is list:
        corpus_name = 'audio file list'
        soundfiles = input_dir
        read_mode = 'list'
    else:
        raise ValueError(
            "ERROR: {} should be a folder, an audio file, or a list of path names!".format(basename(input_dir)))

    print('\nBuilding corpus dictionary from {}'.format(corpus_name))
    counter = Counter(message='        Number of analyzed samples: ')

    # create corpus dictionary
    dictionary = {
        'corpus_info': {
            'max_duration': max_duration,
            'frame_length': frame_length,
            'hop_length': hop_length,
            'data_format': [
                'file_id',
                'sample_index',
                'rms',
                'pitch_centroid'
            ],
            'n_frames': int(),
            'files': list()
        },
        'data_samples': list(),
        'data_tree': dict()
    }
    file_id = 0
    mfcc_frames = list()

    # if input is a folder directory, collect all files from folder and append to soundfiles list
    if read_mode == 'folder':
        [[soundfiles.append(join(root, f)) for f in files] for root, _, files in walk(input_dir)]

    # iterate through paths in soundfiles, select audio files, and extract features
    for sf in soundfiles:
        sf = realpath(sf)
        if splitext(sf)[1] in AUDIO_FORMATS:
            mfcc_stream, metadata, sr = get_features(
                sf, duration=max_duration, n_mfcc=n_mfcc, hop_length=hop_length, frame_length=frame_length)
            for mf, md in zip(mfcc_stream, metadata):
                mfcc_frames.append(mf)
                dictionary['data_samples'].append(
                    np.array(np.concatenate([[file_id],  md])))
            dictionary['corpus_info']['files'].append([sr, sf])
            counter.write(str(file_id + 1))
            file_id += 1

    # build data tree for mfcc frames
    dictionary['data_samples'] = np.array(dictionary['data_samples'])
    n_frames = len(mfcc_frames)
    if kd is None:
        kd = min(n_mfcc, max(int(log(n_frames)/log(4)), 1))
    dictionary['corpus_info']['n_frames'] = n_frames
    dictionary['data_tree'] = build_data_tree(mfcc_frames, kd=kd)
    print('        DONE\n')
    return dictionary

def build_data_tree(data, kd=2):
    print()
    data = np.array(data)
    bar = IncrementalBar('        Classifying data frames: ', max=len(
        data), suffix='%(index)d/%(max)d frames')
    nodes = np.median(data, axis=0)[:kd]
    tree_size = 2**len(nodes)
    tree = {
        'nodes': nodes,
        'dims': kd,
        'position_branches': dict(),
        'data_branches': dict()
    }
    # populate branches
    for i in range(tree_size):
        tree['position_branches'][str(i)] = list()
        tree['data_branches'][str(i)] = list()
    # populate branches
    for pos, datum in enumerate(data):
        branch_id = get_branch_id(datum[:kd], nodes[:kd])
        tree['position_branches'][str(branch_id)].append(pos)
        tree['data_branches'][str(branch_id)].append(datum)
        bar.next()
    # convert branches to numpy arrays
    for b in range(tree_size):
        tree['position_branches'][str(b)] = np.array(
            tree['position_branches'][str(b)])
        tree['data_branches'][str(b)] = np.array(tree['data_branches'][str(b)])
    bar.finish()
    print("        Total number of data clusters: {}".format(tree_size))
    return tree


def neighborhood_index(item, tree):
    kd = tree['dims']
    tree_size = 2**kd
    file_id = get_branch_id(item[:kd], tree['nodes'][:kd])
    default_id = file_id
    z = 1
    while (len(tree['data_branches'][str(file_id)]) == 0):
        file_id = wrap(wedgesum(default_id, z), 0, tree_size)
        z += 1
    return file_id


def wedgesum(a, b):
    if b % 2 == 0:
        b *= -1
    else:
        b += 1
    return a + floor(b/2)


def wrap(a, min, max):
    span = max-min
    return ((a-min) % span) + min


def get_branch_id(vector, nodes):
    size = len(vector)-1
    return sum([0 if v <= n else 2**(size-i) for i, (v, n) in enumerate(zip(vector, nodes))])


def nearest_neighbors(item, data, k=8):
    datasize = len(data)
    if datasize < k:
        k = datasize
    nn = NearestNeighbors(n_neighbors=k, algorithm='brute').fit(data)
    positions = nn.kneighbors(item, n_neighbors=k)[1][0]
    return positions


def get_audio_recipe(target_path, corpus_dict, max_duration=None, n_mfcc=13, hop_length=512, frame_length=1024, k=3):
    '''Takes an audio sample directory/path (i.e. the _target_) and a `dict` object (i.e. the _corpus_), and returns another `dict` object containing the instructions to rebuild the _target_ using grains from the _corpus_. The output can be saved as a `.gamut` file with the `write_gamut()` function, for later use in `cook_recipe()`.'''

    print('\nMaking recipe for {}\n        ...loading corpus...\n        ...analyzing target...'.format(
        basename(target_path)))
    target_mfcc, target_extras, sr = get_features(target_path,
                                                  duration=max_duration,
                                                  n_mfcc=n_mfcc,
                                                  hop_length=hop_length,
                                                  frame_length=frame_length)
    n_samples = len(target_extras)
    dictionary = {
        'target_info': {
            'name': splitext(basename(target_path))[0],
            'sr': sr,
            'frame_length': frame_length,
            'hop_length': hop_length,
            'frame_format': [
                'file_id',
                'sample_index'
            ],
            'data_dims': k,
            'n_samples': n_samples,
            'data_samples': np.empty(shape=(0, 2))
        },
        'corpus_info': corpus_dict['corpus_info'],
        'data_samples': list()
    }

    # include target data samples for cooking mix parameter
    corpus_dict['corpus_info']['files'].append([sr, target_path])
    dictionary['target_info']['data_samples'] = target_extras[:,
                                                              [0, 0]].astype('int32')
    dictionary['target_info']['data_samples'][:, 0] = len(
        corpus_dict['corpus_info']['files']) - 1

    bar = IncrementalBar('        Matching audio frames: ', max=len(
        target_mfcc), suffix='%(index)d/%(max)d frames')

    for tm, tex in zip(target_mfcc, target_extras):
        branch_id = str(neighborhood_index(tm, corpus_dict['data_tree']))
        mfcc_idxs = nearest_neighbors(
            [tm], corpus_dict['data_tree']['data_branches'][branch_id], k=k)
        knn_positions = corpus_dict['data_tree']['position_branches'][branch_id][mfcc_idxs]
        metadata = corpus_dict['data_samples'][knn_positions]
        sorted_positions = nearest_neighbors(
            [tex[1:]], metadata[:, [2, 3]], k=k)
        mfcc_options = metadata[sorted_positions]
        dictionary['data_samples'].append(
            mfcc_options[:, [0, 1]].astype('int32'))
        bar.next()
    bar.finish()
    print('        DONE\n')
    return dictionary


def cook_recipe(recipe_dict, envelope='hann', grain_dur=0.1, stretch_factor=1, onset_var=0, kn=8, n_chans=2, sr=44100, target_mix=0, pan_width=0.5, frame_length_res=512):
    '''Takes a `dict` object (i.e. the _recipe_), and returns an array of audio samples, intended to be written as an audio file.'''

    print('\nCooking recipe for {}\n        ...loading recipe...'.format(
        recipe_dict['target_info']['name']))
    sr_ratio = sr/recipe_dict['target_info']['sr']
    sounds = [[]] * len(recipe_dict['corpus_info']['files'])
    snd_idxs = list()
    [[snd_idxs.append(y[0]) for y in x] for x in recipe_dict['data_samples']]
    snd_idxs = np.unique(snd_idxs).astype(int)
    snd_counter = IncrementalBar('        Loading corpus sounds: ', max=len(
        snd_idxs) + 1, suffix='%(index)d/%(max)d files')
    for i in snd_idxs:
        sounds[i] = np.repeat(np.array([librosa.load(recipe_dict['corpus_info']['files'][i][1],
                              duration=recipe_dict['corpus_info']['max_duration'], sr=sr)[0]]).T, n_chans, axis=1)
        snd_counter.next()
    sounds[-1] = np.repeat(np.array([librosa.load(recipe_dict['corpus_info']
                           ['files'][-1][1], duration=None, sr=sr)[0]]).T, n_chans, axis=1)
    snd_counter.next()
    snd_counter.finish()

    hop_length = int(recipe_dict['target_info']['hop_length'] * sr_ratio)
    data_samples = recipe_dict['data_samples']
    n_segments = recipe_dict['target_info']['n_samples']

    print("        ...creating dynamic control tables...")
    # populate target mix table
    tmix_type = type(target_mix)
    if tmix_type is list:
        target_mix_table = array_resampling(target_mix, n_segments)
    if tmix_type is float or tmix_type is int:
        target_mix_table = np.empty(n_segments)
        target_mix_table.fill(target_mix)

    # populate frame length table
    grain_dur_type = type(grain_dur)
    if grain_dur_type is list:
        frame_length_table = np.round(array_resampling(
            np.array(grain_dur) * sr, n_segments)/frame_length_res) * frame_length_res
    if grain_dur_type is float or grain_dur_type is int:
        frame_length_table = np.empty(n_segments)
        frame_length_table.fill(
            round((grain_dur * sr)/frame_length_res)*frame_length_res)
    frame_length_table = frame_length_table.astype('int64')
    frame_lengths = np.arange(frame_length_res, np.amax(
        frame_length_table)+frame_length_res, frame_length_res, dtype='int64')

    # populate sample index table
    stretch_type = type(stretch_factor)
    if stretch_type is int or stretch_type is float:
        samp_onset_table = np.empty(n_segments)
        samp_onset_table.fill(hop_length*stretch_factor)
    if stretch_type is list:
        samp_onset_table = array_resampling(
            stretch_factor, n_segments)*hop_length
    samp_onset_table = np.concatenate(
        [[0], np.round(samp_onset_table)], ).astype('int64').cumsum()[:-1]

    # apply onset variation table
    onset_var_type = type(onset_var)
    if onset_var_type is float or onset_var_type is int:
        if onset_var > 0:
            jitter = int(max(1, abs((onset_var*sr)/2)))
            onset_var_table = np.random.randint(
                low=jitter*-1, high=jitter, size=n_segments)
            samp_onset_table = samp_onset_table + onset_var_table
    if onset_var_type is list:
        onset_var_table = array_resampling(
            np.array(onset_var)*sr, n_segments) * np.random.rand(n_segments)
        samp_onset_table = samp_onset_table + onset_var_table.astype('int64')
    samp_onset_table[samp_onset_table < 0] = 0

    # compute window with default size
    env_type = type(envelope)
    if env_type == str:
        windows = [np.repeat(np.array(
            [get_window(envelope, Nx=wl)]).T, n_chans, axis=1) for wl in frame_lengths]
    if env_type == np.ndarray or env_type == list:
        windows = [np.repeat(np.array(
            [array_resampling(envelope, N=wl)]).T, n_chans, axis=1) for wl in frame_lengths]

    # compute panning table
    pan_type = type(pan_width)
    pan_table = np.random.randint(low=1, high=16, size=(n_segments, n_chans))
    if pan_type is int or pan_type is float:
        pan_table = pan_table * pan_width
    if pan_type is list:
        pan_table = pan_table * \
            np.repeat(
                np.array([array_resampling(pan_width, n_segments)]).T, n_chans, axis=1)
    pan_table[pan_table < 1] = 1
    row_sums = pan_table.sum(axis=1)
    pan_table = pan_table / row_sums[:, np.newaxis]

    if kn == None:
        kn = recipe_dict['target_info']['frame_dims']
    weigths = np.arange(kn, 0, -1)

    # make buffer array
    buffer = np.empty(
        shape=(int(np.amax(samp_onset_table) + np.amax(frame_length_table)), n_chans))
    buffer.fill(0)

    grain_counter = IncrementalBar('        Concatenating grains:  ', max=len(
        data_samples), suffix='%(index)d/%(max)d grains')

    for n, (ds, so, fl, p, tm) in enumerate(zip(data_samples, samp_onset_table, frame_length_table, pan_table, target_mix_table)):
        if random() > tm:
            num_frames = len(ds[:kn])
            f = choices(ds[:kn], weights=weigths[kn-num_frames:])[0]
        else:
            f = recipe_dict['target_info']['data_samples'][n]
        snd_id = f[0]
        snd = sounds[snd_id]
        snd_sr_ratio = sr/recipe_dict['corpus_info']['files'][snd_id][0]
        max_idx = len(snd) - 1
        samp_st = int(f[1] * snd_sr_ratio)
        samp_end = min(max_idx, samp_st+fl)
        seg_size = round((samp_end-samp_st) /
                         frame_length_res) * frame_length_res
        samp_end = samp_st+seg_size
        if seg_size != 0 and samp_end <= max_idx:
            idx = int(np.where(frame_lengths == seg_size)[0])
            window = windows[idx]
            segment = (snd[samp_st:samp_end] * window) * p
            buffer[so:so+seg_size] = buffer[so:so+seg_size] + segment
        grain_counter.next()

    grain_counter.finish()
    print('        DONE\n')
    # return normalized buffer
    return (buffer / np.amax(np.abs(buffer))) * sqrt(0.5)

if __name__ == '__main__':
    inputs = [
        '/Users/felipe-tovar-henao/Documents/Sample collections/Berklee44v2/',
        '/Users/felipe-tovar-henao/Documents/Sample collections/Berklee44v2/bass_string1.wav',
        ["/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Bass_Tuba/blow/BTb-blow-N-p-N-N.wav" ,
        "/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Bass_Tuba/breath/BTb-breath-N-pp-N-N.wav" ,
        "/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Bass_Tuba/flatterzunge/BTb-flatt-E4-pp-N-N.wav" ,
        "/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Bass_Tuba/ordinario/BTb-ord-E4-pp-N-N.wav" ,
        "/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Horn/flatterzunge/Hn-flatt-E4-pp-N-N.wav" ,
        "/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Horn/ordinario/Hn-ord-E4-pp-N-N.wav" ,
        "/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Trombone/flatterzunge/Tbn-flatt-E4-pp-N-N.wav" ,
        "/Users/felipe-tovar-henao/Desktop/Orchestral_corpus/Brass/Trombone/ordinario/Tbn-ord-E4-pp-N-N.wav"]
    ]
    build_corpus(inputs[1])
