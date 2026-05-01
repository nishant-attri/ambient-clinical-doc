from backend.structuring import extract_structured_note
from backend.validation import validate_evidence

transcript = """
Doctor: What brings you in today?
Patient: I've been having chest pain for the last 3 days.
Doctor: Any history of heart disease?
Patient: No.
Doctor: Are you taking any medications?
Patient: No.
"""

result = extract_structured_note(transcript)

validation = validate_evidence(result, transcript)

print("\nSTRUCTURED OUTPUT:")
print(result.model_dump())

print("\nVALIDATION:")
print(validation)