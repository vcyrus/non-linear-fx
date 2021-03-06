import librosa
import numpy as np
import os
from scipy import signal

import meta

def load_audio(path, idx=None, total=None, fx=None):
    if idx and total and fx:
        print('loading {0} / {1}: {3} {2}'.format(idx + 1, total, path, fx))
    else:
        print('loading {0}'.format(path))
    audio, _ = librosa.load(path, sr=meta.params_data['fs'], mono=meta.params_data['mono'])
#     audio = normalize_audio(audio)
#     audio, _ = librosa.effects.trim(audio) # remove leading and trailing silences
    audio = audio.T
    audio = np.reshape(audio, [-1, 1])
    return audio

def normalize_audio(audio):
    mean = np.mean(audio)
    audio -= mean
    maximum = max(abs(audio))

    return audio / maximum

def get_input_target_fname_pairs(instrument=meta.BASS, effect=meta.DISTORTION, fx_param_id=meta.fx_param_ids[0]):
    audio_ids = get_file_audio_ids(meta.params_path[instrument][meta.NO_FX])

    return [(fname, target) for target in os.listdir(meta.params_path[instrument][effect]) 
                            for (fname, f_prefix) in audio_ids 
                            if get_fname_param_id(target).endswith(fx_param_id) and target.startswith(f_prefix)]

def get_fxchain_fname_pairs(instrument=meta.BASS, param_setting='1'):
    audio_ids = get_file_audio_ids(meta.params_path[meta.FXCHAIN][instrument][meta.NO_FX])
    
    return [(fname, target) for target in os.listdir(meta.params_path[meta.FXCHAIN][instrument][param_setting])
                            for (fname, f_prefix) in audio_ids
                            if target.startswith(f_prefix)
           ]

def get_file_audio_ids(path):
    ''' Get the file id in the first half of the file name.
        This half of the filename identifies the audio clip (with or without effect).
        The second half identifies the unique file.
        
        Example file name: B12-55412-4413-07592.wav
        The first half identifies the audio. The second half is a unique file identifier.
        Many files may have the same first half if there are multiple effects applied to an audio clip.
        
        This function returns the first half identifier, used to match dry and wet samples of the same audio clip.
    '''
    assert os.path.isdir(os.path.dirname(path)), "path to feature directory does not exist"
    
    file_list = os.listdir(path)
    f_audio_ids = [(fname, get_fname_prefix(fname)) for fname in file_list \
                   if fname.endswith(meta.suffix) and os.path.isfile(os.path.join(path, fname))]
    
    return f_audio_ids

def get_fname_prefix(fname):
    '''Returns first half of formatted file name, e.g B12-55412-4413-07592.wav -> B12-55412
    '''
    return meta.params_data['separator'].join(fname.replace(meta.suffix, '').split(meta.params_data['separator'])[0:2]) 

def get_fname_param_id(fname):
    ''' Extract the part of filename giving parameter number: e.g B12-55412-4413-07592.wav -> 4413 -> 3
    '''
    return fname.split(meta.params_data['separator'])[2]

def get_target_files(f_id, fx_path):
    ''' f_id: as generated by get_file_audio_ids from the NoFX samples, e.g 'B11-35107'
        Files beginning with the same prefix ID are corresponding processed audio samples
    '''
    return [f for f in os.listdir(fx_path) if f.startswith(f_id)]

def get_dir_files(path):
    return os.listdir(path)

def overlap_sum(input, nstep):
    nperseg = input.shape[1]
    nseg = input.shape[0]
    outputlength = nperseg + (nseg-1)*nstep
    x = np.zeros(outputlength)
    norm = np.zeros(outputlength)
    win = signal.windows.hann(nperseg)
    
    for i in range(nseg):
        x[i*nstep:i*nstep+nperseg] += input[i]*win
        norm[i*nstep:i*nstep+nperseg] += win**2
    #x /= np.where(norm > 1e-10, norm, 1.0)
    return x

def get_model_path(instrument, fx, fx_param_id, model_num):
    return os.path.join(meta.path_models, '{0}_{1}_{2}_{3}/'.format(instrument, fx, fx_param_id, model_num))

