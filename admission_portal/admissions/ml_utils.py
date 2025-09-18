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

def normalize_features(feature_map: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure all REQUIRED_FEATURE_ORDER fields exist.
    Uppercase strings, leave numeric values as-is, fill missing numeric with 0.
    """
    normalized = {}
    for k in REQUIRED_FEATURE_ORDER:
        v = feature_map.get(k)
        if v is None:
            # Fill missing values
            if k in ["Age at Enrollment", "Requirement Agreement", "Disability", "Indigenous"]:
                normalized[k] = 0
            else:
                normalized[k] = ""
        else:
            # Only uppercase strings
            normalized[k] = v.upper().strip() if isinstance(v, str) else v
    return normalized

def predict_student_rf(profile: Dict[str, Any]) -> Dict[str, Any]:
    """Predict probability and class for a single student profile dict."""
    model = _load_model()
    normalized = normalize_features(profile)

    df = pd.DataFrame([[normalized[k] for k in REQUIRED_FEATURE_ORDER]], columns=REQUIRED_FEATURE_ORDER)
    global _last_prediction_error
    try:
        if model is not None:
            pred = model.predict(df)[0]
            proba = float(model.predict_proba(df)[0][1]) if hasattr(model, "predict_proba") else 0.7 if int(pred) == 1 else 0.3
            return {"Prediction": int(pred), "Probability": proba}
        else:
            return {"Prediction": 0, "Probability": 0.5}  # fallback if model not loaded
    except Exception as exc:
        _last_prediction_error = exc
        logger.exception("Prediction failed; returning fallback: %s", exc)
        return {"Prediction": 0, "Probability": 0.5}

def compute_and_save_enrollment_chance(student: Student) -> float:
    """
    Compute enrollment probability for a single Django Student instance
    and save it to the enrollment_chance column.
    """
    from .utils import build_flat_record  # your existing helper that flattens student data
    try:
        feature_map = build_flat_record(student)
        normalized_features_map = normalize_features(feature_map)
        pred_dict = predict_student_rf(normalized_features_map)
        student.enrollment_chance = pred_dict["Probability"]
        student.save(update_fields=["enrollment_chance"])
        return pred_dict["Probability"]
    except Exception as exc:
        logger.exception("Failed to compute enrollment chance for student %s: %s", student.id, exc)
        return student.enrollment_chance if student.enrollment_chance is not None else 0.5
