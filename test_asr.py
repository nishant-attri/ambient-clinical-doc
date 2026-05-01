import time
from backend.asr import transcribe_audio

start = time.time()
result = transcribe_audio("sample_audio.mp3")
end = time.time()

print(f"Time taken: {end - start:.2f} seconds")