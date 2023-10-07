import librosa
import numpy as np

def normalize_audio(data):
    md = np.mean(data)
    sd = np.std(data)
    data = (data - md) / sd
    return data


def readAudio(audio_path, fs_target=22050):

    audio, fs = librosa.load(audio_path, mono=True, sr=fs_target)
    # logger.info("lenght: {} s".format(len(data) / fs), {"task_id": task_id})

    return (normalize_audio(audio), fs)

def readAudio_by_segment(audio_path, fs_target=22050, start=None, end=None):

    duration_all = librosa.get_duration(path=audio_path)

    if start is not None and end is None:
        audio, fs = librosa.load(audio_path, mono=True, sr=fs_target, offset=start, duration=duration_all-start)
    elif start is not None and end is not None:
        audio, fs = librosa.load(audio_path, mono=True, sr=fs_target, offset=start, duration=end - start)
    else:
        audio, fs = librosa.load(audio_path, mono=True, sr=fs_target)

    # logger.info("lenght: {} s".format(len(data) / fs), {"task_id": task_id})

    return (normalize_audio(audio), fs, duration_all)


def read_all_bytes(filename):
    in_file = open(filename, "rb")
    bytes = in_file.read()
    in_file.close()
    return bytes