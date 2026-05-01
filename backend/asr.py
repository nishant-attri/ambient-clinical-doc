from faster_whisper import WhisperModel

# Load model once (important for performance)
model = WhisperModel("small", compute_type="int8")

def transcribe_audio(file_path: str):
    segments, info = model.transcribe(file_path)

    full_text = ""
    segment_list = []

    for segment in segments:
        full_text += segment.text + " "
        segment_list.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })

    return {
        "full_text": full_text.strip(),
        "segments": segment_list
    }