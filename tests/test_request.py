import librosa
import io
import requests
import time
from utils.serializers import ndarray_to_bytes

def max_request(signal, url, topN=None) -> dict:
    audio_bytes = ndarray_to_bytes(signal)
    buf = io.BytesIO()
    buf.write(audio_bytes)
    # sf.write(buf, signal, fs, format='WAV', endian='LITTLE', subtype='PCM_16')
    buf.seek(0)
    
    if topN is not None:
        url += '?topN={:d}'.format(topN)
        
    response = (requests.post(url, files={"audio": buf})).json()
    # print(response.json())
    
    return response["predictions"], response["music_score"]


if __name__ == "__main__":
    #file = "/home/joao/Desktop/Ecad/database/audio/tasks/139743/139743.ogg"
    file = '/mnt/dev/dirceusilva/dados/Cover/setlist_65k/audio/tasks/139850/139850.ogg' 
    url_base = "http://localhost:5000/model/predict/bytes"

    signal, fs = librosa.load(file, mono=True, sr=16000)
    segment_signal = signal[:int(10 * fs)]
    segment_duration = 10  # 10s
    topN = 5

    samples_per_segment = fs * segment_duration
    num_segments = len(signal) // samples_per_segment
    start = time.time()
    predictions = []
    music_score = []
    for i in range(num_segments):
        start_sample = i * samples_per_segment
        end_sample = (i + 1) * samples_per_segment
        segment_signal = signal[start_sample:end_sample]
        classes, music_prob = max_request(signal=segment_signal, url=url_base, topN=topN)
        predictions.append({"classes":classes, "music_score": music_prob, "inicio":float(start_sample)/fs, "fim":float(end_sample)/fs })
        music_score.append(music_prob)
        
    # max_request(signal=signal)
    print(predictions)
    print(f"{time.time()-start}")
    print(f"Segment {num_segments}")