from os.path import realpath, basename, isdir, splitext, join
from os import walk, rename
from math import floor, log, sqrt
from random import choices, random
import numpy as np
import librosa
from scipy.signal import get_window
from sklearn.neighbors import NearestNeighbors
from progress.bar import IncrementalBar
from progress.counter import Counter
from soundfile import write
import sounddevice as sd

np.seterr(divide='ignore')

FILE_EXT = '.gamut'
AUDIO_FORMATS = ['.wav', '.aif', '.aiff']

def dict_to_gamut(dict, output_dir):
    '''Writes `dict` object into a `.gamut` file. This function is a simple wrapper of `np.save()`.'''
    output_dir = splitext(output_dir)[0]
    np.save(output_dir, dict)
    rename(output_dir+'.npy', output_dir+FILE_EXT)

def dict_from_gamut(input_dir):
    '''Reads a `.gamut` file as a `dict` object. This function is a simple wrapper of `np.load()`.'''
    ext = basename(input_dir)[-6:]
    if ext == FILE_EXT:
        return np.load(input_dir, allow_pickle=True).item()
    else:
        raise ValueError(
            'Wrong file extension. Provide a directory for a {} file'.format(FILE_EXT))

def write_audio(output_dir, ndarray, sr=44100, bit_depth=24):
    """Writes a `ndarray` as audio. This function is a simple wrapper of `sf.write()`."""
    ext = splitext(output_dir)[1]
    if ext not in AUDIO_FORMATS:
        raise ValueError('Output file format must be .wav, .aif, or .aiff')
    write(output_dir, ndarray, sr, 'PCM_{}'.format(bit_depth))

def play_audio(ndarray, sr=44100):
    sd.play(ndarray, samplerate=sr)
    sd.wait()

def array_resampling(array, N):
    x_coor1 = np.arange(0, len(array)-1, (len(array)-1)/N)[:N]
    x_coor2 = np.arange(0, len(array))
    return np.interp(x_coor1, x_coor2, array)

def get_features(input_dir, max_duration=None, n_mfcc=13, hop_length=512, frame_length=1024):
    '''Returns a 3-tuple of ndarrays, consisting of:
            - MFCC frames of audio target (ndarray)
            - Audio target meta-data (ndarray) - i.e. [`sample_index`, `rms_amplitude`, `pitch_centroid`]
            - Sampling rate of target (int).'''
    input_dir = realpath(input_dir)
    y, sr = librosa.load(input_dir, duration=max_duration, sr=None)
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
    '''Takes a folder directory, or an audio file directory, or a list of directories to audio files, and returns a `dict` object. The output can be saved as a `.gamut` file with the `dict_to_gamut()` function, for later use in `get_audio_recipe()`.'''

    soundfiles = list()

    # check if input_dir is folder or list of s
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
            'n_mfcc': n_mfcc,
            'hop_length': hop_length,
            'frame_length': frame_length,
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
        [[soundfiles.append(join(root, f)) for f in files]
         for root, _, files in walk(input_dir)]

    # iterate through paths in soundfiles, select audio files, and extract features
    for sf in soundfiles:
        sf = realpath(sf)
        if splitext(sf)[1] in AUDIO_FORMATS:
            mfcc_stream, metadata, sr = get_features(
                sf, max_duration=max_duration, n_mfcc=n_mfcc, hop_length=hop_length, frame_length=frame_length)
            for mf, md in zip(mfcc_stream, metadata):
                mfcc_frames.append(mf)
                dictionary['data_samples'].append(
                    np.array(np.concatenate([[file_id],  md])))
            dictionary['corpus_info']['files'].append([sr, sf])
            counter.next()
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

def find_nodes(data, depth=0, kd=None, medians=None, nodes=list(), count=1):
	N = len(data)
	# initialize nodes
	if len(nodes) == 0:
		nodes = [[]]*kd	
    # pass global median to branch if branch is empty
	if N <= 0:
		if depth < kd:
			nodes[depth] = nodes[depth]+[[medians[depth], count]]		
		return nodes
    # split branches recursively when depth < kd
	if depth < kd:
		sorted_data = data[data[:, depth].argsort()]
		split = floor(int(N/2))
		node = sorted_data[split][depth]
		if node is not None:
			nodes[depth] = nodes[depth]+[[node, count]]
		find_nodes(sorted_data[:split], depth+1, kd=kd, medians=medians, nodes=nodes, count=count*2)
		find_nodes(sorted_data[split + 1:], depth+1, kd=kd, medians=medians, nodes=nodes, count=count*2+1)
		return nodes
	else:
		return nodes # stop recursion

def sort_nodes(tree_nodes, medians=None):
	return [[(n[j][0] if n[j][1] == (2**i)+j else medians[i]) if j < len(n) else medians[i] for j in range(2**i)] for i, n in enumerate(tree_nodes)]

def get_branch_id(vector, nodes):
    idx = 0
    for i, v in enumerate(vector):
        node = nodes[i][idx]
        idx = (idx << 1) | 1 if v > node else idx << 1
    return idx

def fit_data(data, data_min=list(), data_max=list()):
    if len(data_min) * len(data_max) == 0:
        data_min = np.amin(data, axis=0)
        data_max = np.amax(data, axis=0)
    return (data-data_min)/(data_max-data_min), data_min, data_max

def build_data_tree(data, kd=2):
    '''Creates a KDTree data structure.'''
    print()
    data, data_min, data_max = fit_data(np.array(data))
    bar = IncrementalBar('        Classifying data frames: ', max=len(
        data), suffix='%(index)d/%(max)d frames')
    medians = np.median(data, axis=0)
    nodes = sort_nodes(find_nodes(data, kd=kd, medians=medians), medians=medians)
    tree_size = 2**len(data[0][:kd])
    tree = {
        'nodes': nodes,
        'dims': kd,
        'data_min': data_min,
        'data_max': data_max,
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
    b = (b * -1) if (b % 2 == 0) else (b + 1)
    return a + floor(b/2)


def wrap(a, min, max):
    return ((a-min) % max-min) + min

def nearest_neighbors(item, data, kn=8):
    datasize = len(data)
    if datasize < kn:
        kn = datasize
    nn = NearestNeighbors(n_neighbors=kn, algorithm='brute').fit(data)
    dx, positions = nn.kneighbors(item, n_neighbors=kn)
    return positions[0], dx[0]

def get_audio_recipe(target_dir, corpus_dict, max_duration=None, hop_length=512, frame_length=1024, kn=8):
    '''Takes an audio sample directory/path (i.e. the _target_) and a `dict` object (i.e. the _corpus_), and returns another `dict` object containing the instructions to rebuild the _target_ using grains from the _corpus_. The output can be saved as a `.gamut` file with the `dict_to_gamut()` function, for later use in `cook_recipe()`.'''

    print('\nMaking recipe for {}\n        ...loading corpus...\n        ...analyzing target...'.format(
        basename(target_dir)))
    target_mfcc, target_extras, sr = get_features(target_dir,
                                                  max_duration=max_duration,
                                                  n_mfcc=corpus_dict['corpus_info']['n_mfcc'],
                                                  hop_length=hop_length,
                                                  frame_length=frame_length)
    target_mfcc = fit_data(target_mfcc, data_min=corpus_dict['data_tree']['data_min'], data_max=corpus_dict['data_tree']['data_max'])[0]
    n_samples = len(target_extras)
    dictionary = {
        'target_info': {
            'name': splitext(basename(target_dir))[0],
            'sr': sr,
            'frame_length': frame_length,
            'hop_length': hop_length,
            'frame_format': [
                'file_id',
                'sample_index'
            ],
            'data_dims': kn,
            'n_samples': n_samples,
            'data_samples': np.empty(shape=(0, 2))
        },
        'corpus_info': corpus_dict['corpus_info'],
        'data_samples': list()
    }

    # include target data samples for cooking mix parameter
    corpus_dict['corpus_info']['files'].append([sr, target_dir])
    dictionary['target_info']['data_samples'] = target_extras[:,[0, 0]].astype('int32')
    dictionary['target_info']['data_samples'][:, 0] = len(corpus_dict['corpus_info']['files']) - 1

    error_sum = 0
    bar = IncrementalBar('        Matching audio frames: ', max=len(target_mfcc), suffix='%(index)d/%(max)d frames')
    for tm, tex in zip(target_mfcc, target_extras):
        branch_id = str(neighborhood_index(tm, corpus_dict['data_tree']))
        mfcc_idxs, dx = nearest_neighbors([tm], corpus_dict['data_tree']['data_branches'][branch_id], kn=kn)
        error_sum += dx[0]
        knn_positions = corpus_dict['data_tree']['position_branches'][branch_id][mfcc_idxs]
        metadata = corpus_dict['data_samples'][knn_positions]
        sorted_positions = nearest_neighbors([tex[1:]], metadata[:, [2, 3]], kn=kn)[0]
        mfcc_options = metadata[sorted_positions]
        dictionary['data_samples'].append(mfcc_options[:, [0, 1]].astype('int32'))
        bar.next()
    bar.finish()
    error_sum = int((error_sum/n_samples)*1000)/1000
    print('        Delta average: {}\n        DONE.\n'.format(error_sum))
    return dictionary

def cook_recipe(recipe_dict, grain_dur=0.1, stretch_factor=1, onset_var=0, target_mix=0, pan_depth=5, kn=8, n_chans=2, envelope='hann', sr=None, frame_length_res=512):
    '''Takes a `dict` object (i.e. the _recipe_), and returns an array of audio samples, intended to be written as an audio file.'''

    print('\nCooking recipe for {}\n        ...loading recipe...'.format(
        recipe_dict['target_info']['name']))
    # if None, use sr from recipe
    if sr is None:
        sr = recipe_dict['target_info']['sr']
        sr_ratio = 1
    else:
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
    if tmix_type in [list, np.ndarray]:
        target_mix_table = array_resampling(target_mix, n_segments)
    if tmix_type in [int, float]:
        target_mix_table = np.empty(n_segments)
        target_mix_table.fill(target_mix)

    # populate frame length table
    grain_dur_type = type(grain_dur)
    if grain_dur_type in [list, np.ndarray]:
        frame_length_table = np.round(array_resampling(
            np.array(grain_dur) * sr, n_segments)/frame_length_res) * frame_length_res
    if grain_dur_type in [int, float]:
        frame_length_table = np.empty(n_segments)
        frame_length_table.fill(
            round((grain_dur * sr)/frame_length_res)*frame_length_res)
    frame_length_table = frame_length_table.astype('int64')
    frame_lengths = np.arange(frame_length_res, np.amax(
        frame_length_table)+frame_length_res, frame_length_res, dtype='int64')

    # populate sample index table
    stretch_type = type(stretch_factor)
    if stretch_type in [int, float]:
        samp_onset_table = np.empty(n_segments)
        samp_onset_table.fill(hop_length*stretch_factor)
    if stretch_type in [list, np.ndarray]:
        samp_onset_table = array_resampling(
            stretch_factor, n_segments)*hop_length
    samp_onset_table = np.concatenate(
        [[0], np.round(samp_onset_table)], ).astype('int64').cumsum()[:-1]

    # apply onset variation table
    onset_var_type = type(onset_var)
    if onset_var_type in [int, float]:
        if onset_var > 0:
            jitter = int(max(1, abs((onset_var*sr)/2)))
            onset_var_table = np.random.randint(
                low=jitter*-1, high=jitter, size=n_segments)
            samp_onset_table = samp_onset_table + onset_var_table
    if onset_var_type in [list, np.ndarray]:
        onset_var_table = array_resampling(
            np.array(onset_var)*sr, n_segments) * np.random.rand(n_segments)
        samp_onset_table = samp_onset_table + onset_var_table.astype('int64')
    samp_onset_table[samp_onset_table < 0] = 0

    # compute window with default size
    env_type = type(envelope)
    if env_type == str:
        windows = [np.repeat(np.array(
            [get_window(envelope, Nx=wl)]).T, n_chans, axis=1) for wl in frame_lengths]
    if env_type in [list, np.ndarray]:
        windows = [np.repeat(np.array(
            [array_resampling(envelope, N=wl)]).T, n_chans, axis=1) for wl in frame_lengths]

    # compute panning table
    pan_depth = max(0, pan_depth)
    pan_type = type(pan_depth)
    if pan_type in [list, np.ndarray]:
        pan_depth = np.repeat(np.array([array_resampling(np.array(pan_depth), n_segments)]).T, n_chans, axis=1)
    pan_table = 1 / np.power(2, pan_depth * np.abs(np.repeat(np.array([np.linspace(0, 1, n_chans)]), n_segments, axis=0) - np.random.rand(n_segments, 1)))
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
        seg_size = round((samp_end-samp_st) / frame_length_res) * frame_length_res
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
    print()
