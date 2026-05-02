# 🏥 Ambient Clinical Documentation Pipeline

An AI-powered pipeline that automatically converts doctor-patient consultation audio into structured clinical notes — eliminating the need for manual documentation.

🔗 **Live Demo:** [clinical-transcription.streamlit.app](https://clinical-transcription.streamlit.app)

---

## 📌 Overview

Doctors spend a significant portion of their time on administrative documentation rather than patient care. This project addresses that problem by building an **ambient clinical documentation system** — a doctor records a consultation, and the system automatically produces a clean, structured clinical note.

The pipeline works in three stages:
1. **Transcription** — converts audio to text using a local speech recognition model
2. **Structuring** — extracts clinical fields from the raw conversation using an LLM
3. **Validation** — verifies that every extracted field is grounded in the transcript

---

## 🎬 Demo

Upload a clinical consultation audio file and the app will generate:

- 📝 Full transcript of the consultation
- 🗂️ Structured clinical note with organised sections
- 🔍 Evidence map linking each field to its source quote
- ✅ Validation result confirming all fields are transcript-grounded

---

## 🏗️ Architecture

```
Audio File
    │
    ▼
┌─────────────────────────┐
│   ASR Module            │  faster-whisper (local)
│   Audio → Transcript    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Structuring Module    │  Google Gemini 2.5 Flash
│   Transcript → Schema   │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Validation Module     │  Custom grounding check
│   Schema → Verified     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Streamlit Frontend    │  Public web interface
│   Results → UI          │
└─────────────────────────┘
```

---

## 🧠 Clinical Schema

The pipeline extracts the following fields from each consultation:

| Field | Description |
|---|---|
| `patient_info` | Patient demographic details |
| `chief_complaint` | Primary reason for the visit |
| `history_present_illness` | Concise clinical summary of symptoms |
| `past_medical_history` | Previously diagnosed conditions |
| `medications` | Current medications |
| `allergies` | Known allergies |
| `social_history` | Lifestyle and social factors |
| `family_history` | Relevant family medical history |
| `review_of_systems` | Symptom review across body systems |
| `assessment` | Doctor's clinical assessment |
| `plan` | Treatment plan |
| `follow_up` | Follow-up instructions |
| `evidence_map` | Source quotes for each extracted field |

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Speech Recognition | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) |
| LLM | [Google Gemini 2.5 Flash Lite](https://ai.google.dev/) |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) |
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) |
| Frontend | [Streamlit](https://streamlit.io/) |
| Deployment | [Streamlit Community Cloud](https://streamlit.io/cloud) |

---

## 🚀 Running Locally

### Prerequisites
- Python 3.9+
- A [Gemini API key](https://aistudio.google.com/app/apikey) (free tier)

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/nishant-attri/ambient-clinical-doc.git
cd ambient-clinical-doc
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Create a `.env` file in the project root**
```
GEMINI_API_KEY=your_api_key_here
```

**4. Run the Streamlit app**
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Running the FastAPI backend separately (optional)
```bash
uvicorn backend.main:app --reload
```

API will be available at `http://127.0.0.1:8000`

---

## 📁 Project Structure

```
ambient-clinical-doc/
├── backend/
│   ├── __init__.py
│   ├── asr.py            # Speech recognition module
│   ├── models.py         # Pydantic clinical schema
│   ├── structuring.py    # LLM-based note extraction
│   ├── validation.py     # Evidence grounding validation
│   └── main.py           # FastAPI endpoint
├── app.py                # Streamlit frontend
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Key Design Decisions

**No hallucination policy** — the LLM is strictly instructed to extract only explicitly stated information. Fields like `assessment` and `plan` are left null unless the doctor explicitly states them — even when a diagnosis is clinically obvious from the conversation.

**Evidence grounding validation** — every extracted field is cross-checked against the original transcript to ensure the information is traceable to a real quote, not inferred or fabricated.

**Local ASR** — faster-whisper runs entirely on-device, meaning audio never leaves the user's machine during transcription. This is an important privacy consideration for medical data.

---

## 🔮 Future Improvements

- Improve `history_present_illness` summarisation conciseness
- Populate `review_of_systems` more reliably from doctor's symptom review
- Add speaker diarisation to separate doctor and patient speech
- Support real-time streaming transcription
- Add PDF export of the structured clinical note
- Add user authentication for multi-user deployment

---

## 👤 Author

**Nishant Attri**
[GitHub](https://github.com/nishant-attri)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
