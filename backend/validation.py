import re

def normalize_text(text: str) -> str:
    """Lowercase and remove extra whitespace and punctuation for comparison."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # replace punctuation with space
    text = re.sub(r'\s+', ' ', text)       # collapse multiple spaces
    return text.strip()


def validate_evidence(clinical_note, transcript: str):

    issues = []
    normalized_transcript = normalize_text(transcript)

    for field, snippet in clinical_note.evidence_map.items():
        if not snippet:
            continue

        # Normalize the snippet and split into individual words
        words = normalize_text(snippet).split()

        # Filter out very short words (like "a", "the", "is")
        meaningful_words = [w for w in words if len(w) > 3]

        if len(meaningful_words) == 0:
            continue

        words_found = sum(1 for word in meaningful_words if word in normalized_transcript)
        match_ratio = words_found / len(meaningful_words)

        if match_ratio < 0.6:
            issues.append(f"{field}: evidence not grounded in transcript")

    return {
        "is_valid": len(issues) == 0,
        "issues": issues
    }

