import librosa
import base64
import io
import soundfile as sf
import requests

file = "/home/joao/Desktop/Ecad/database/audio/tasks/test/test.ogg"
url = "http://localhost:3004/model/predict/base64"
signal, fs = librosa.load(file, mono=True, sr=16000)

# Duration of each audio segment to be sent in seconds
segment_duration = 10  # 10s

# Number of samples per segment
samples_per_segment = fs * segment_duration

# Total number of segments
num_segments = len(signal) // samples_per_segment

# Loop through the signal with a step size of 10s worth of samples
for i in range(num_segments):
    start_sample = i * samples_per_segment
    end_sample = (i + 1) * samples_per_segment
    
    # Extract the segment from the signal
    segment_signal = signal[start_sample:end_sample]
    
    # Save the segment to a BytesIO buffer
    buf = io.BytesIO()
    sf.write(buf, segment_signal, fs, format='WAV', endian='LITTLE', subtype='PCM_16')
    
    # Encode to base64
    audio_base64_bytes = base64.b64encode(buf.getvalue())
    audio_base64_string = audio_base64_bytes.decode('utf-8')
    
    # Send the segment as a POST request
    post_data = {"audio": audio_base64_string}
    response = requests.post(url, json=post_data)
    
    # Output the response from the server
    print(f"Segment {i+1}/{num_segments}")
    print(response.status_code)
    print(response.json())