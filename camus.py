from os.path import realpath, basename, isdir, splitext, join
from os import walk
import librosa
import json
from librosa.util.utils import frame
from numba.core.decorators import jit
import numpy as np
from numpy import inf, int64
from math import floor, log
from random import randint, choices
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

    y, sr = librosa.load(file_path, duration=duration)

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

    return mfcc_frames, metadata, len(y)

def build_corpus(corpus_path, duration=None, n_mfcc=13, hop_length=512, frame_length=1024, kd=None):
    corpus_path = realpath(corpus_path)
    corpus_name = basename(corpus_path)

    if isdir(corpus_path):
        print('...building corpus dictionary from {}...'.format(corpus_name))
        db = {
            'corpus_info': {
                'corpus_name': corpus_name,
                'max_duration': duration,
                'frame_length': frame_length,
                'hop_length': hop_length,
                'data_format': [
                    'path_id',
                    'sample_index',
                    'RMS',
                    'centroid_pitch'
                ],
                'n_frames': int(),
                'paths': list()
            },
            'data_samples': list(),
            'KDTree': dict()
        }
        path_id = 0
        mfcc_frames = list()
        for path, _, files in walk(corpus_path):
            for f in files:
                file_ext = splitext(f)[1]
                if file_ext == '.wav' or file_ext == '.aif' or file_ext == '.aiff':
                    file_path = join(path, f)
                    db['corpus_info']['paths'].append(file_path)
                    mfcc_stream, metadata, _ = get_features(file_path, duration=duration, n_mfcc=n_mfcc, hop_length=hop_length, frame_length=frame_length)
                    for mf, md in zip(mfcc_stream, metadata):
                        mfcc_frames.append(mf)
                        db['data_samples'].append([path_id] + md.tolist())
                    path_id += 1
        n_frames = len(mfcc_frames)
        if kd is None:
            kd = max(int(log(n_frames)/log(4)), 1)
        db['corpus_info']['n_frames'] = n_frames
        db['KDTree'] = build_KDTree(mfcc_frames, kd=kd)
        print('\nDONE building corpus {}.json'.format(corpus_name))
        return db
    else:
        raise ValueError("ERROR: {} must be a folder!".format(basename(corpus_path)))

def get_audio_recipe(target_path, corpus_db, duration=None, n_mfcc=13, hop_length=512, frame_length=1024, k=3):
    print('    ...loading corpus...')
    corpus_dict = load_JSON(corpus_db)
    print('    ...analyzing target...')
    target_mfcc, target_extras, target_size = get_features(target_path,
                        duration=duration,
                        n_mfcc=n_mfcc,
                        hop_length=hop_length,
                        frame_length=frame_length)    
    dictionary = {
        'target_info': {
            'frame_length': frame_length,
            'hop_length': hop_length,
            'frame_format': [
                'path_id', 
                'sample_index'
            ],
            'data_dims': k,
            'target_size': target_size,
            'n_samples': len(target_mfcc)
        },
        'corpus_info': corpus_dict['corpus_info'],
        'data_samples': list()
    } 

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
    path_id = get_branch_id(item[:kd], tree['nodes'][:kd])
    default_id = path_id
    flag = True
    z = 1
    while flag:
        if len(tree['data_branches'][str(path_id)]) > 0:
            flag = False
        else:
            path_id = wrap(wedgesum(default_id, z), 0, tree_size)
            z += 1
    return path_id

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

def cook_recipe(recipe_path, envelope='hann', frame_length=1024, stretch_factor=1, jitter=512, kn=8):
    print('...loading recipe...')

    recipe_dict = load_JSON(recipe_path)
    hop_length = int(recipe_dict['target_info']['hop_length'] * stretch_factor)

    print('...loading corpus sounds...')

    max_duration = recipe_dict['corpus_info']['max_duration']
    sounds = [librosa.load(p, duration=max_duration)[0] for p in recipe_dict['corpus_info']['paths']]
    frames = recipe_dict['data_samples']
    segments = list()

    if kn == None:
        kn = recipe_dict['target_info']['frame_dims']
    weigths = np.arange(kn, 0, -1)
    for fs in frames:
        num_frames = len(fs[:kn])
        f = choices(fs[:kn], weights=weigths[kn-num_frames:])[0]
        snd = sounds[f[0]]
        samp_st = f[1]
        segment = snd[samp_st:samp_st+frame_length]
        segments.append(segment)

    return concat_segments(segments, envelope=envelope, hop_length=hop_length, jitter=jitter, max_frame_length=frame_length, total_samples=recipe_dict['target_info']['target_size'])

def cook_recipe_2(recipe_path, envelope='hann', frame_length=1024, stretch_factor=1, jitter=512, kn=8, n_chans=2):
    print('...loading recipe...')
    recipe_dict = load_JSON(recipe_path)

    print('...loading corpus sounds...')
    max_duration = recipe_dict['corpus_info']['max_duration']
    sounds = [librosa.load(p, duration=max_duration)[0] for p in recipe_dict['corpus_info']['paths']]
    hop_length = int(recipe_dict['target_info']['hop_length'])
    data_samples = recipe_dict['data_samples']

    n_segments = recipe_dict['target_info']['n_samples']
    # populate frame length table
    if type(frame_length) is list:
        frame_length_table = np.round(array_resampling(frame_length, n_segments))
    if type(frame_length) is int:
        frame_length_table = np.empty(n_segments)
        frame_length_table.fill(frame_length) 
    frame_length_table = frame_length_table.astype('int64')

    # populate sample index table   
    if type(stretch_factor) is int or type(stretch_factor) is float:
        samp_onset_table = np.empty(n_segments)
        samp_onset_table.fill(hop_length*stretch_factor)
    if type(stretch_factor) is list:
        samp_onset_table = array_resampling(stretch_factor, n_segments)*hop_length   
    samp_onset_table = np.concatenate([[0], np.round(samp_onset_table)]).astype('int64').cumsum()[:-1]    

    # populate jitter table
    if jitter == 0:
        jitter_table = np.zeros(n_segments, dtype=int)
    else:
        jitter = int(max(1, abs(jitter/2)))
        jitter_table = np.random.randint(low=jitter*-1, high=jitter, size=n_segments)
        samp_onset_table = samp_onset_table + jitter_table
        samp_onset_table[samp_onset_table < 0] = 0
    
    # get total duration
    output_length = int(samp_onset_table[-1] + np.amax(frame_length_table))

    # make output array
    output = np.empty(shape=(output_length, n_chans))
    output.fill(0)

    # compute window with default size
    env_type = type(envelope)
    default_length = scipy.stats.mode(frame_length_table)[0]
    if env_type == str:
        window = get_window(envelope, Nx=default_length)
    if env_type == np.ndarray or env_type == list:
        window = array_resampling(envelope, N=default_length)
    window = np.repeat(np.array([window]).T, n_chans, axis=1)

    # compute panning vable
    pan_table = np.random.randint(low=1, high=16, size=(n_segments, n_chans))
    row_sums = pan_table.sum(axis=1)
    pan_table = pan_table / row_sums[:, np.newaxis]
    
    if kn == None:
        kn = recipe_dict['target_info']['frame_dims']
    weigths = np.arange(kn, 0, -1)

    for ds, so, fl, p in zip(data_samples, samp_onset_table, frame_length_table, pan_table):
        num_frames = len(ds[:kn])
        f = choices(ds[:kn], weights=weigths[kn-num_frames:])[0]
        snd = sounds[f[0]]
        max_idx = len(snd) - 1
        samp_st = f[1]
        samp_end = min(max_idx, samp_st+fl)
        segment = np.repeat(np.array([snd[samp_st:samp_end]]).T, n_chans, axis=1)
        seg_size = len(segment)
        if seg_size != len(window):
            segment = segment * resample(window, seg_size)
        else:
            segment = segment * window
        output[so:so+seg_size] = output[so:so+seg_size] + (segment * p)

    # return normalized output
    return (output / np.amax(np.abs(output))) * 0.707946

def array_resampling(array, N):
        x_coor1 = np.arange(0, len(array)-1, (len(array)-1)/N)
        x_coor2 = np.arange(0, len(array))
        return np.interp(x_coor1, x_coor2, array)

def concat_segments(segments, envelope='hann', hop_length=512, jitter=64, n_chans=2, max_frame_length=1024, total_samples=None):
    n_segments = len(segments)
    outsize = total_samples + jitter + max_frame_length
    output = np.zeros((outsize, n_chans))
    jitsize = int(jitter/2)
    envtype = type(envelope)
    if envtype == str:
        window = np.repeat(np.array([get_window(envelope, Nx=max_frame_length)]).T, n_chans, axis=1)
    if envtype == np.ndarray or envtype == list:
        window = np.repeat(np.array([resample(envelope, num=max_frame_length)]).T, n_chans, axis=1)
    panning = np.random.randint(1, 16, size=(n_segments, n_chans))
    for i, (seg, pan) in enumerate(zip(segments, panning)):
        segsize = len(seg)
        st = max(0, (i*hop_length)+randint(-jitsize, jitsize))
        end = min(st + segsize, outsize-1)
        seg = np.repeat(np.array([seg]).T, n_chans, axis=1)
        pan = pan/np.sum(pan)
        if segsize != len(window):
            seg = seg * resample(window, segsize)
        else:
            seg = seg * window
        output[st:end] = output[st:end] + (seg * pan)
    return output

def nearest_neighbors(item, data, k=8):
    datasize = len(data)
    if datasize < k:
        k = datasize
    nn = NearestNeighbors(n_neighbors=k, algorithm='brute').fit(data)
    positions = np.array(nn.kneighbors(np.array([item]), n_neighbors=k)[1][0])
    return positions

if __name__ == '__main__':
    print('----- running utilities.py')
    a = np.array([
        [0, 0],
        [1, 2],
        [2,3],
        [4,5]
    ])
    b = np.array([2,2])
    print(a*b)
