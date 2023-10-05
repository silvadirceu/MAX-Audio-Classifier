import librosa
import io
import requests
import time
from utils.serializers import ndarray_to_bytes

def max_request(signal, topN=5) -> dict:
    audio_bytes = ndarray_to_bytes(signal)
    buf = io.BytesIO()
    buf.write(audio_bytes)
    # sf.write(buf, signal, fs, format='WAV', endian='LITTLE', subtype='PCM_16')
    buf.seek(0)

    response = requests.post(url, files={"audio": buf})
    # print(response.json())
    return response.json()["predictions"]


if __name__ == "__main__":
    file = "/home/joao/Desktop/Ecad/database/audio/tasks/139743/139743.ogg"
    url = "http://localhost:3005/model/predict/bytes"

    signal, fs = librosa.load(file, mono=True, sr=16000)
    segment_signal = signal[:int(10 * fs)]
    segment_duration = 10  # 10s
    topN = 5

    if topN is not None:
        url += '?topN='+topN

    samples_per_segment = fs * segment_duration
    num_segments = len(signal) // samples_per_segment
    start = time.time()
    predictions = []
    for i in range(num_segments):
        start_sample = i * samples_per_segment
        end_sample = (i + 1) * samples_per_segment
        segment_signal = signal[start_sample:end_sample]
        predictions.extend(max_request(signal=segment_signal))

    # max_request(signal=signal)
    print(predictions)
    print(f"{time.time()-start}")
    print(f"Segment {num_segments}")