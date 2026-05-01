from pydantic import BaseModel
from typing import Optional, Dict, List

class ClinicalNote(BaseModel):
    patient_info: Optional[Dict] = None
    chief_complaint: Optional[str] = None
    history_present_illness: Optional[str] = None
    past_medical_history: List[str] = []
    medications: List[str] = []
    allergies: List[str] = []
    social_history: Optional[Dict] = None
    family_history: Optional[str] = None
    review_of_systems: Optional[Dict] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    follow_up: Optional[str] = None
    evidence_map: Dict[str, str] = {}