import os
from dotenv import load_dotenv
load_dotenv()
import json
import google.generativeai as genai
from backend.models import ClinicalNote

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash-lite")


def clean_json_response(text: str):
    text = text.strip()

    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines)

    return text.strip()


def filter_evidence_map(evidence_map: dict):
    allowed_keys = {
        "patient_info",
        "chief_complaint",
        "history_present_illness",
        "past_medical_history",
        "medications",
        "allergies",
        "social_history",
        "family_history",
        "review_of_systems",
        "assessment",
        "plan",
        "follow_up"
    }
    return {k: v for k, v in evidence_map.items() if k in allowed_keys}


def extract_structured_note(transcript: str, max_retries: int = 2):

    schema_str = json.dumps(ClinicalNote.model_json_schema(), indent=2)

    prompt = (
    "You are a clinical documentation assistant. Your job is to convert a raw "
    "doctor-patient conversation transcript into a clean, professional clinical note.\n\n"
    
    "STRICT RULES:\n"
    "- Extract ONLY explicitly stated information from the transcript.\n"
    "- DO NOT infer or assume anything not directly stated.\n"
    "- If a field is not mentioned, return null or empty list.\n"
    "- DO NOT generate assessment or plan unless explicitly stated by the doctor.\n"
    "- DO NOT fabricate medications or diagnoses.\n\n"
    
    "WRITING STYLE RULES — VERY IMPORTANT:\n"
    "- Write in clean, professional clinical language.\n"
    "- DO NOT copy verbatim sentences from the transcript.\n"
    "- DO NOT include filler words like 'like', 'um', 'yeah', 'I think', 'I guess'.\n"
    "- Summarise and paraphrase into concise clinical statements.\n"
    "- Write in third person (e.g. 'Patient reports...' not 'I've been...').\n"
    "- Keep each field concise — 1 to 3 sentences maximum.\n\n"
    
    "FIELD GUIDELINES:\n"
    "- chief_complaint: One short phrase — the primary reason for the visit.\n"
    "- history_present_illness: Concise clinical summary of onset, duration, "
    "character, associated symptoms. Maximum 3 sentences.\n"
    "- past_medical_history: List of confirmed conditions only. Empty list if none.\n"
    "- medications: List of confirmed medications only. Empty list if none.\n"
    "- allergies: List of confirmed allergies only. Empty list if none.\n"
    "- family_history: One concise sentence summarising relevant family conditions.\n\n"
    
    "SOCIAL HISTORY FORMAT:\n"
    "- Return structured fields like:\n"
    '  {"living_situation": "...", "smoking": "...", "alcohol": "...", '
    '"drugs": "...", "sexual_activity": "..."}\n'
    "- Write concise clinical statements, not quotes from the transcript.\n"
    "- Do NOT use questions as keys.\n\n"
    
    "REVIEW OF SYSTEMS:\n"
    "- If the doctor asked about specific symptoms and the patient responded, "
    "populate this field.\n"
    "- Format as a dictionary with symptom as key and response as value.\n"
    '- Example: {"headache": "denied", "fever": "denied", "cough": "denied"}\n\n'
    
    "EVIDENCE MAP RULES:\n"
    "- evidence_map MUST use ONLY these keys:\n"
    '  ["patient_info", "chief_complaint", "history_present_illness",\n'
    '   "past_medical_history", "medications", "allergies",\n'
    '   "social_history", "family_history", "review_of_systems",\n'
    '   "assessment", "plan", "follow_up"]\n'
    "- Each key should map to ONE short supporting quote from the transcript.\n"
    "- If a field is null or empty, DO NOT include it in evidence_map.\n"
    "- Do NOT create new keys.\n"
    "- Evidence must be an exact substring from the transcript.\n"
    "- Evidence snippets must be SHORT — 1 sentence maximum.\n\n"
    
    "Return ONLY valid JSON. Do not include markdown or code blocks.\n\n"
    "Schema:\n"
    + schema_str +
    "\n\nTranscript:\n"
    + transcript
)

    for attempt in range(max_retries + 1):

        response = model.generate_content(prompt)

        try:
            cleaned_text = clean_json_response(response.text)
            print("\n=== CLEANED TEXT ===")
            print(cleaned_text)
            print("====================\n")

            structured_data = json.loads(cleaned_text)
            structured_data["evidence_map"] = filter_evidence_map(
                structured_data.get("evidence_map", {})
            )

            validated = ClinicalNote(**structured_data)

            # Remove evidence map entries for fields that are empty or null
            cleaned_evidence = {}
            for field, snippet in validated.evidence_map.items():
                field_value = getattr(validated, field, None)
                # Keep evidence only if the field actually has content
                if field_value is not None and field_value != [] and field_value != {}:
                    cleaned_evidence[field] = snippet

            validated.evidence_map = cleaned_evidence

            return validated

        except Exception as e:
            print(f"[Attempt {attempt}] Failed parsing: {e}")
            print("Raw output:", response.text)

            if attempt == max_retries:
                raise ValueError("LLM failed after retries")