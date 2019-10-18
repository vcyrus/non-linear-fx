import librosa
import numpy as np
import os

from meta import *

def load_audio(path, data_params):
    audio, _ = librosa.load(path, sr=data_params['fs'], mono=data_params['mono'])

    audio = audio.T
    audio = np.reshape(audio, [-1, 1])
    return audio

def normalize_audio(audio):
    mean = np.mean(audio)
    audio -= mean
    max = max(abs(audio))

    return audio / max

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
    f_audio_ids = [params_data['separator'].join(fname.replace(suffix, '').split(params_data['separator'])[0:2]) 
                       for fname in file_list if fname.endswith(suffix) and os.path.isfile(os.path.join(path, fname))]
    
    return f_audio_ids

def get_target_files(f_id, fx_path):
    ''' f_id: as generated by get_file_audio_ids from the NoFX samples, e.g 'B11-35107'
        Files beginning with the same prefix ID are corresponding processed audio samples
    '''
    return [f for f in os.listdir(fx_path) if f.startswith(f_id)]
    
    
