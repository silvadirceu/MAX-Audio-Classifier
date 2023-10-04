import librosa
import numpy as np

def normalize_audio(data):
    md = np.mean(data)
    sd = np.std(data)
    data = (data - md) / sd
    return data


def read_audio(audio_path):
    audio, fs = librosa.load(audio_path, mono=True, sr=22050)
    # logger.info("lenght: {} s".format(len(data) / fs), {"task_id": task_id})
    return (normalize_audio(audio), fs)


def read_all_bytes(filename):
    in_file = open(filename, "rb")
    bytes = in_file.read()
    in_file.close()
    return bytes