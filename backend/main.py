from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os

from backend.asr import transcribe_audio
from backend.structuring import extract_structured_note
from backend.validation import validate_evidence

app = FastAPI()

UPLOAD_DIR = "temp_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}


@app.post("/process-consultation")
async def process_consultation(file: UploadFile = File(...)):

    # --- Guard 1: Check file type ---
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_extension}'. Please upload an audio file (mp3, wav, m4a, ogg, flac)."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # --- Step 1: ASR ---
    try:
        asr_result = transcribe_audio(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )

    # --- Guard 2: Check transcript is not empty ---
    if not asr_result["full_text"].strip():
        raise HTTPException(
            status_code=422,
            detail="Transcription produced no text. The audio may be silent or too short."
        )

    # --- Step 2: Structuring ---
    try:
        structured_note = extract_structured_note(asr_result["full_text"])
    except ValueError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Structuring failed: {str(e)}"
        )

    # --- Step 3: Validation ---
    try:
        validation_result = validate_evidence(
            structured_note,
            asr_result["full_text"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation failed: {str(e)}"
        )

    # --- Cleanup: Remove uploaded file after processing ---
    os.remove(file_path)

    return {
        "transcript": asr_result["full_text"],
        "structured_note": structured_note.model_dump(),
        "validation": validation_result
    }