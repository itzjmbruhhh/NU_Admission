import pandas as pd
import joblib
import os
import logging
from django.conf import settings
from typing import Dict, Any
from .models import Student

logger = logging.getLogger(__name__)

_model = None
_model_load_error = None
_last_prediction_error: Exception | None = None

REQUIRED_FEATURE_ORDER = [
    "School Term", "Age at Enrollment", "Requirement Agreement", "Disability", "Indigenous",
    "Program (First Choice)", "Program (Second Choice)", "Entry Level", "Birth City", "Place of Birth (Province)",
    "Gender", "Citizen of", "Religion", "Civil Status", "Current Region", "Current Province", "City/Municipality",
    "Current Brgy.", "Permanent Country", "Permanent Region", "Permanent Province", "Permanent City", "Permanent Brgy.",
    "Birth Country", "Student Type", "School Type"
]

def _load_model():
    global _model, _model_load_error
    if _model is not None or _model_load_error is not None:
        return _model
    try:
        path = os.path.join(settings.BASE_DIR, 'admissions', 'resources', 'rf_ucModel.pkl')
        _model = joblib.load(path)
        logger.info("Loaded RF model from %s", path)
    except Exception as exc:
        _model_load_error = exc
        _model = None
        logger.error("Failed to load RF model: %s", exc)
    return _model

def capitalize_contents(data: Any) -> Any:
    """Recursively uppercase all string leaves in dict/list structures."""
    if isinstance(data, dict):
        return {k: capitalize_contents(v) for k, v in data.items()}
    if isinstance(data, list):
        return [capitalize_contents(v) for v in data]
    if isinstance(data, str):
        return data.upper()
    return data

def predict_student_rf(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict class and probability for a single student profile dict,
    exactly like the original JSON script approach.
    """
    model = _load_model()
    # Uppercase everything recursively to match JSON behavior
    profile = capitalize_contents(profile)

    # Convert to DataFrame with required columns
    df = pd.DataFrame([profile])

    global _last_prediction_error
    try:
        if model is not None:
            pred = model.predict(df)[0]
            proba = float(model.predict_proba(df)[0][1]) if hasattr(model, "predict_proba") else 0.7 if int(pred) == 1 else 0.3
            return {"Prediction": int(pred), "Probability": proba}
        else:
            return {"Prediction": 0, "Probability": 0.5}
    except Exception as exc:
        _last_prediction_error = exc
        logger.exception("Prediction failed; returning fallback: %s", exc)
        return {"Prediction": 0, "Probability": 0.5}

def compute_and_save_enrollment_chance(student: Student) -> float:
    """
    Compute enrollment probability for a single Student instance,
    using exactly the JSON-script logic, and save it to enrollment_chance.
    """
    from .utils import build_flat_record
    try:
        feature_map = build_flat_record(student)
        pred_dict = predict_student_rf(feature_map)
        # Store as percentage (0..100)
        student.enrollment_chance = float(pred_dict["Probability"]) * 100.0
        student.save(update_fields=["enrollment_chance"])
        return student.enrollment_chance
    except Exception as exc:
        logger.exception("Failed to compute enrollment chance for student %s: %s", student.id, exc)
        return student.enrollment_chance if student.enrollment_chance is not None else 50.0
