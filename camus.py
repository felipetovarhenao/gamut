from os.path import realpath, basename, isdir, splitext, join
from os import walk, rename
import librosa
import numpy as np
from numpy import inf
from math import floor, log, sqrt
from random import choices, random
from scipy.stats import mode
from scipy.signal import get_window, resample
from sklearn.neighbors import NearestNeighbors
from progress.bar import IncrementalBar
from progress.counter import Counter
from soundfile import write

np.seterr(divide='ignore')

FILE_EXT = '.camus'

def dict_to_camus(dict, outpath):
    '''Writes `dict` object into a `.camus` file. This function is a simple wrapper of `np.save()`.'''
    np.save(outpath, dict)
    rename(outpath+'.npy', outpath+FILE_EXT)

def dict_from_camus(path):
    '''Reads a `.camus` file as a `dict` object. This function is a simple wrapper of `np.load()`.'''
    ext = basename(path)[-6:]
    if ext == FILE_EXT:
        return np.load(path, allow_pickle=True).item()
    else:
        raise ValueError('Wrong file extension. Provide a path for a {} file'.format(FILE_EXT))

def write_audio(path, ndarray, sr=44100, bit_depth=24):
    """Writes a `ndarray` as audio. This function is a simple wrapper of `sf.write()`."""
    write(path, ndarray, sr, 'PCM_{}'.format(bit_depth))

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
    centroid_frames[centroid_frames == -inf] = 0                                                
    n_frames = len(rms_frames)
    sample_indxs = np.arange(start=0, stop=n_frames*hop_length, step=hop_length)
    metadata = np.array([sample_indxs, rms_frames, centroid_frames]).T

    return mfcc_frames, metadata, sr

def build_corpus(folder_dir, duration=None, n_mfcc=13, hop_length=512, frame_length=1024, kd=None):
    '''Takes a folder directory (i.e. a path) containing audio samples (`.wav`, `.aif`, or `.aiff`) and returns a `dict` object. The output can be saved as a `.camus` file with the `write_camus()` function, for later use in `get_audio_recipe()`.'''

    folder_dir = realpath(folder_dir)
    corpus_name = basename(folder_dir)
    if isdir(folder_dir):
        print('\nBuilding corpus dictionary from {}'.format(corpus_name))
        counter = Counter(message='        Number of analyzed samples: ')
        dictionary = {
            'corpus_info': {
                'name': corpus_name,
                'max_duration': duration,
                'frame_length': frame_length,
                'hop_length': hop_length,
                'data_format': [
                    'file_id',
                    'sample_index',
                    'RMS',
                    'centroid_pitch'
                ],
                'n_frames': int(),
                'files': list()
            },
            'data_samples': list(),
            'KDTree': dict()
        }
        file_id = 0
        mfcc_frames = list()
        for path, _, files in walk(folder_dir):
            for f in files:
                file_ext = splitext(f)[1]
                if file_ext == '.wav' or file_ext == '.aif' or file_ext == '.aiff':
                    file_path = join(path, f)
                    mfcc_stream, metadata, sr = get_features(file_path, duration=duration, n_mfcc=n_mfcc, hop_length=hop_length, frame_length=frame_length)
                    for mf, md in zip(mfcc_stream, metadata):
                        mfcc_frames.append(mf)
                        dictionary['data_samples'].append(np.array(np.concatenate([[file_id],  md])))
                    dictionary['corpus_info']['files'].append([sr, file_path])
                    counter.write(str(file_id + 1))
                    file_id += 1
        dictionary['data_samples'] = np.array(dictionary['data_samples'])
        n_frames = len(mfcc_frames)
        if kd is None:
            kd = max(int(log(n_frames)/log(4)), 1)
        dictionary['corpus_info']['n_frames'] = n_frames
        dictionary['KDTree'] = build_KDTree(mfcc_frames, kd=kd)
        print('        DONE\n')
        return dictionary
    else:
        raise ValueError("ERROR: {} must be a folder!".format(basename(folder_dir)))

def build_KDTree(data, kd=2):
    print()
    data = np.array(data)
    bar = IncrementalBar('        Classifying data frames: ', max=len(data), suffix='%(index)d/%(max)d frames')
    nodes = np.median(data, axis=0)[:kd]
    tree_size =2**len(nodes)
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
        branch_id = get_branch_id(datum[:kd], nodes)
        tree['position_branches'][str(branch_id)].append(pos)
        tree['data_branches'][str(branch_id)].append(datum)
        bar.next()
    # convert branches to numpy arrays
    for b in range(tree_size):
        tree['position_branches'][str(b)] = np.array(tree['position_branches'][str(b)])
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
    return sum([0 if v <= n else 2**(size-i) for i, (v, n) in enumerate(zip(vector,nodes))])

def get_audio_recipe(target_path, corpus_dict, duration=None, n_mfcc=13, hop_length=512, frame_length=1024, k=3):
    '''Takes an audio sample directory/path (i.e. the _target_) and a `dict` object (i.e. the _corpus_), and returns another `dict` object containing the instructions to rebuild the _target_ using grains from the _corpus_. The output can be saved as a `.camus` file with the `write_camus()` function, for later use in `cook_recipe()`.'''

    print('\nMaking recipe for {}\n        ...loading corpus...\n        ...analyzing target...'.format(basename(target_path)))
    target_mfcc, target_extras, sr = get_features(target_path,
                                                            duration=duration,
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
    dictionary['target_info']['data_samples'] = target_extras[:,[0, 0]].astype('int32')
    dictionary['target_info']['data_samples'][:, 0] = len(corpus_dict['corpus_info']['files']) - 1

    bar = IncrementalBar('        Matching audio frames: ', max=len(target_mfcc), suffix='%(index)d/%(max)d frames')

    for tm, tex in zip(target_mfcc, target_extras):
        branch_id = str(neighborhood_index(tm, corpus_dict['KDTree']))
        mfcc_idxs = nearest_neighbors([tm], corpus_dict['KDTree']['data_branches'][branch_id], k=k)
        knn_positions = corpus_dict['KDTree']['position_branches'][branch_id][mfcc_idxs]
        metadata = corpus_dict['data_samples'][knn_positions]
        sorted_positions = nearest_neighbors([tex[1:]], metadata[:,[2,3]],k=k)
        mfcc_options = metadata[sorted_positions]
        dictionary['data_samples'].append(mfcc_options[:,[0,1]].astype('int32'))
        bar.next()
    bar.finish()
    print('        DONE\n')
    return dictionary

def nearest_neighbors(item, data, k=8):
    datasize = len(data)
    if datasize < k:
        k = datasize
    nn = NearestNeighbors(n_neighbors=k, algorithm='brute').fit(data)
    positions = nn.kneighbors(item, n_neighbors=k)[1][0]
    return positions

def cook_recipe(recipe_dict, envelope='hann', grain_dur=0.1, stretch_factor=1, onset_var=0, kn=8, n_chans=2, sr=44100, target_mix=0, stereo=0.5):
    '''Takes a `dict` object (i.e. the _recipe_), and returns an array of audio samples, intended to be written as an audio file.'''

    print('\nCooking recipe for {}\n        ...loading recipe...'.format(recipe_dict['target_info']['name']))
    target_sr = recipe_dict['target_info']['sr']
    sr_ratio = sr/target_sr
     
    corpus_size = len(recipe_dict['corpus_info']['files'])
    sounds = [[]] * corpus_size
    snd_idxs = list()
    [[snd_idxs.append(y[0]) for y in x] for x in recipe_dict['data_samples']]
    snd_idxs = np.unique(snd_idxs).astype(int)    
    max_duration = recipe_dict['corpus_info']['max_duration']
    snd_counter = IncrementalBar('        Loading corpus sounds: ', max=len(snd_idxs) + 1, suffix='%(index)d/%(max)d files')
    for i in snd_idxs:
        sounds[i] = np.repeat(np.array([librosa.load(recipe_dict['corpus_info']['files'][i][1], duration=max_duration, sr=sr)[0]]).T, n_chans, axis=1)
        snd_counter.next()
    sounds[-1] = np.repeat(np.array([librosa.load(recipe_dict['corpus_info']['files'][-1][1], duration=None, sr=sr)[0]]).T, n_chans, axis=1)
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
    if type(grain_dur) is list:
        frame_length_table = np.round(array_resampling(np.array(grain_dur) * sr, n_segments))
    if type(grain_dur) is float or type(grain_dur) is int:
        frame_length_table = np.empty(n_segments)
        frame_length_table.fill(grain_dur * sr) 
    frame_length_table = frame_length_table.astype('int64')

    # populate sample index table   
    if type(stretch_factor) is int or type(stretch_factor) is float:
        samp_onset_table = np.empty(n_segments)
        samp_onset_table.fill(hop_length*stretch_factor)
    if type(stretch_factor) is list:
        samp_onset_table = array_resampling(stretch_factor, n_segments)*hop_length   
    samp_onset_table = np.concatenate([[0], np.round(samp_onset_table)], ).astype('int64').cumsum()[:-1]
    
    # apply onset variation table   
    onset_var_type = type(onset_var)
    if onset_var_type is float or onset_var_type is int:
        if onset_var > 0:
            jitter = int(max(1, abs((onset_var*sr)/2)))
            onset_var_table = np.random.randint(low=jitter*-1, high=jitter, size=n_segments)
            samp_onset_table = samp_onset_table + onset_var_table
    if onset_var_type is list:
        onset_var_table = array_resampling(np.array(onset_var)*sr, n_segments) * np.random.rand(n_segments)
        samp_onset_table = samp_onset_table + onset_var_table.astype('int64')
    samp_onset_table[samp_onset_table < 0] = 0

    # compute window with default size
    env_type = type(envelope)
    default_length = int(mode(frame_length_table)[0])
    if env_type == str:
        window = get_window(envelope, Nx=default_length)
    if env_type == np.ndarray or env_type == list:
        window = array_resampling(envelope, N=default_length)
    window = np.repeat(np.array([window]).T, n_chans, axis=1)

    # compute panning table
    pan_type = type(stereo)
    pan_table = np.random.randint(low=1, high=16, size=(n_segments, n_chans))
    if pan_type is int or pan_type is float:
        pan_table = pan_table * stereo
    if pan_type is list:
        pan_table = pan_table * np.repeat(np.array([array_resampling(stereo, n_segments)]).T, n_chans, axis=1)
    pan_table[pan_table < 1] = 1
    row_sums = pan_table.sum(axis=1)
    pan_table = pan_table / row_sums[:, np.newaxis]

    if kn == None:
        kn = recipe_dict['target_info']['frame_dims']
    weigths = np.arange(kn, 0, -1)

    # get total duration
    buffer_length = int(np.amax(samp_onset_table) + np.amax(frame_length_table))

    # make buffer array
    buffer = np.empty(shape=(buffer_length, n_chans))
    buffer.fill(0)

    grain_counter = IncrementalBar('        Concatenating grains:  ', max=len(data_samples), suffix='%(index)d/%(max)d grains')
    for n, (ds, so, fl, p, tm) in enumerate(zip(data_samples, samp_onset_table, frame_length_table, pan_table, target_mix_table)):
        if random() > tm:
            num_frames = len(ds[:kn])
            f = choices(ds[:kn], weights=weigths[kn-num_frames:])[0]
        else:
            f = recipe_dict['target_info']['data_samples'][n]
        snd_id = f[0]
        snd = sounds[snd_id]
        snd_sr = recipe_dict['corpus_info']['files'][snd_id][0]
        snd_sr_ratio = sr/snd_sr
        max_idx = len(snd) - 1
        samp_st = int(f[1] * snd_sr_ratio)
        samp_end = min(max_idx, samp_st+fl)
        segment = snd[samp_st:samp_end]
        seg_size = len(segment)
        if seg_size != len(window):
            segment = segment * resample(window, seg_size)
        else:
            segment = segment * window
        buffer[so:so+seg_size] = buffer[so:so+seg_size] + (segment*p)
        grain_counter.next()

    grain_counter.finish()
    print('        DONE\n')    
    # return normalized buffer
    return (buffer / np.amax(np.abs(buffer))) * sqrt(0.5)

def array_resampling(array, N):
    x_coor1 = np.arange(0, len(array)-1, (len(array)-1)/N)
    x_coor2 = np.arange(0, len(array))
    return np.interp(x_coor1, x_coor2, array)
