from os.path import realpath, basename, isdir, splitext, join
from os import walk
import librosa
import json
import numpy as np
from numpy import inf
from math import floor, log
from random import choices, random
import scipy
from scipy.signal import get_window, resample
from sklearn.neighbors import NearestNeighbors

def save_JSON(dict, outpath):
    with open(outpath, 'w') as fp:
        json.dump(dict, fp, indent=4)

def load_JSON(file):
    with open(file, 'r') as fp:
        return json.load(fp)

def get_features(file_path, duration=None, n_mfcc=13, hop_length=512, frame_length=1024):
    file_path = realpath(file_path)

    print('\n        ...loading {}...'.format(basename(file_path)))
    y, sr = librosa.load(file_path, duration=duration, sr=None)

    print('       ...analyzing sample...')
    mfcc_frames = librosa.feature.mfcc(y=y,
                                    sr=sr, 
                                    n_mfcc=n_mfcc, 
                                    n_fft=frame_length, 
                                    hop_length=hop_length).T[:-2]

    print('        ...computing extra features...')
    rms_frames = librosa.feature.rms(y=y, 
                                    frame_length=frame_length, 
                                    hop_length=hop_length)[0][:-2]
                                    
    centroid_frames = np.log2(librosa.feature.spectral_centroid(y=y,
                                                    sr=sr,
                                                    n_fft=frame_length,
                                                    hop_length=hop_length)[0][:-2]/440)*12+69
    centroid_frames[centroid_frames == -inf] = 0                                                
    n_frames = np.shape(rms_frames)[0]
    sample_indxs = np.arange(start=0, stop=n_frames*hop_length, step=hop_length)
    metadata = np.array([sample_indxs, rms_frames, centroid_frames]).T

    print('    TOTAL NUMBER OF FRAMES: {}'.format(n_frames))

    return mfcc_frames, metadata, len(y), sr

def build_corpus(folder_dir, duration=None, n_mfcc=13, hop_length=512, frame_length=1024, kd=None):
    folder_dir = realpath(folder_dir)
    corpus_name = basename(folder_dir)

    if isdir(folder_dir):
        print('...building corpus dictionary from {}...'.format(corpus_name))
        db = {
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
                    mfcc_stream, metadata, _, sr = get_features(file_path, duration=duration, n_mfcc=n_mfcc, hop_length=hop_length, frame_length=frame_length)
                    for mf, md in zip(mfcc_stream, metadata):
                        mfcc_frames.append(mf)
                        db['data_samples'].append([file_id] + md.tolist())
                    db['corpus_info']['files'].append([sr, file_path])
                    file_id += 1
        n_frames = len(mfcc_frames)
        if kd is None:
            kd = max(int(log(n_frames)/log(4)), 1)
        db['corpus_info']['n_frames'] = n_frames
        db['KDTree'] = build_KDTree(mfcc_frames, kd=kd)
        print('\nDONE building corpus {}.json'.format(corpus_name))
        return db
    else:
        raise ValueError("ERROR: {} must be a folder!".format(basename(folder_dir)))

def get_audio_recipe(target_path, corpus_db, duration=None, n_mfcc=13, hop_length=512, frame_length=1024, k=3):
    print('    ...loading corpus...')
    corpus_dict = load_JSON(corpus_db)
    print('    ...analyzing target...')
    target_mfcc, target_extras, target_size, sr = get_features(target_path,
                                                            duration=duration,
                                                            n_mfcc=n_mfcc,
                                                            hop_length=hop_length,
                                                            frame_length=frame_length)    
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
            'target_size': target_size,
            'n_samples': len(target_mfcc),
            'data_samples': list()
        },
        'corpus_info': corpus_dict['corpus_info'],
        'data_samples': list()
    } 

    # include target data samples for cooking mix parameter
    file_id = len(corpus_dict['corpus_info']['files'])
    corpus_dict['corpus_info']['files'].append([sr, target_path])
    [dictionary['target_info']['data_samples'].append([file_id, int(te[0])]) for te in target_extras]

    corpus_metadata = np.array(corpus_dict['data_samples'])

    corpus_tree = corpus_dict['KDTree']
    tree_size = 2**corpus_tree['dims']

    corpus_tree_posns = [np.array(corpus_tree['position_branches'][str(x)], dtype='int') for x in range(tree_size)]
    corpus_tree_mfccs = [np.array(corpus_tree['data_branches'][str(x)], dtype='int') for x in range(tree_size)]

    print('    ...finding best matches...')

    for tm, tex in zip(target_mfcc, target_extras):
        branch_id = neighborhood_index(tm, corpus_tree)
        mfcc_indxs = nearest_neighbors(tm, corpus_tree_mfccs[branch_id], k=k)
        original_positions = [corpus_tree_posns[branch_id][j] for j in mfcc_indxs]
        metadata = corpus_metadata[original_positions]
        sorted_positions = nearest_neighbors(tex[1:], metadata[:,[2,3]],k=k)
        mfcc_options = metadata[sorted_positions]
        dictionary['data_samples'].append(mfcc_options[:,[0,1]].astype(int).tolist())

    print('DONE making recipe')
    return dictionary

def build_KDTree(data, kd=2):
    print('    ...building KDTree with {} branches...'.format(2**kd))
    data = np.array(data)
    nodes = np.median(data, axis=0)[:kd]
    tree_size =2**len(nodes)
    tree = {
        'nodes': nodes.tolist(),
        'dims': kd,
        'position_branches': dict(),
        'data_branches': dict()
    }
    for i in range(tree_size):
        tree['position_branches'][str(i)] = list()
        tree['data_branches'][str(i)] = list()
    print("    ...populating branches...")
    for pos, datum in enumerate(data):
        branch_id = get_branch_id(datum[:kd], nodes)
        tree['position_branches'][str(branch_id)].append(pos)
        tree['data_branches'][str(branch_id)].append(datum.tolist())

    print("    KDTree built")
    return tree

def neighborhood_index(item, tree):
    kd = tree['dims']
    tree_size = 2**kd
    file_id = get_branch_id(item[:kd], tree['nodes'][:kd])
    default_id = file_id
    flag = True
    z = 1
    while flag:
        if len(tree['data_branches'][str(file_id)]) > 0:
            flag = False
        else:
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

def cook_recipe(recipe_path, envelope='hann', grain_dur=0.1, stretch_factor=1, onset_var=0, kn=8, n_chans=2, sr=44100, target_mix=0.5, stereo=0.5):
    print('...loading recipe...')
    recipe_dict = load_JSON(recipe_path)
    target_sr = recipe_dict['target_info']['sr']
    sr_ratio = sr/target_sr
     
    print('...loading corpus sounds...')
    corpus_size = len(recipe_dict['corpus_info']['files'])
    sounds = [[]] * corpus_size
    snd_idxs = np.unique(np.concatenate([[y[0] for y in x] for x in recipe_dict['data_samples']]))
    snd_idxs[-1] = corpus_size - 1
    max_duration = recipe_dict['corpus_info']['max_duration']
    for i in snd_idxs:
        # load and, when necessary, resample sounds to buffer sampling rate.
        sounds[i] = librosa.load(recipe_dict['corpus_info']['files'][i][1], duration=max_duration, sr=sr)[0]

    print("...creating dynamic control tables...")
    hop_length = int(recipe_dict['target_info']['hop_length'] * sr_ratio) 
    data_samples = recipe_dict['data_samples']
    n_segments = recipe_dict['target_info']['n_samples']

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
    samp_onset_table = np.concatenate([[0], np.round(samp_onset_table)]).astype('int64').cumsum()[:-1]    

    # populate jitter table
    jitter = int(onset_var * sr)
    if jitter > 0:
        jitter = int(max(1, abs((jitter*sr_ratio)/2)))
        jitter_table = np.random.randint(low=jitter*-1, high=jitter, size=n_segments)
        samp_onset_table = samp_onset_table + jitter_table
        samp_onset_table[samp_onset_table < 0] = 0
    
    # get total duration
    buffer_length = int(np.amax(samp_onset_table) + np.amax(frame_length_table))

    # make buffer array
    buffer = np.empty(shape=(buffer_length, n_chans))
    buffer.fill(0)

    # compute window with default size
    env_type = type(envelope)
    default_length = int(scipy.stats.mode(frame_length_table)[0])
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

    print("...concatenating grains...")
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
        segment = np.repeat(np.array([snd[samp_st:samp_end]]).T, n_chans, axis=1)
        seg_size = len(segment)
        if seg_size != len(window):
            segment = segment * resample(window, seg_size)
        else:
            segment = segment * window
        buffer[so:so+seg_size] = buffer[so:so+seg_size] + (segment*p)

    # return normalized buffer
    return (buffer / np.amax(np.abs(buffer))) * 0.707946

def array_resampling(array, N):
        x_coor1 = np.arange(0, len(array)-1, (len(array)-1)/N)
        x_coor2 = np.arange(0, len(array))
        return np.interp(x_coor1, x_coor2, array)

def nearest_neighbors(item, data, k=8):
    datasize = len(data)
    if datasize < k:
        k = datasize
    nn = NearestNeighbors(n_neighbors=k, algorithm='brute').fit(data)
    positions = np.array(nn.kneighbors(np.array([item]), n_neighbors=k)[1][0])
    return positions

if __name__ == '__main__':
    print('----- running utilities.py')
