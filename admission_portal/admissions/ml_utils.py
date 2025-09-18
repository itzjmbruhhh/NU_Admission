"""Machine Learning utilities (deprecated).

This module previously handled Random Forest probability predictions for
enrollment chance. The application has removed predictive scoring logic
and currently does not call these functions. They are retained only for
potential future re‑enablement or reference. Safe to delete if ML is
permanently retired.
"""

import json
import joblib
import os
from django.conf import settings
from typing import Tuple, Any, Dict
import pandas as pd

MODEL_PATH = os.path.join(settings.BASE_DIR, "admissions", "resources", "rf_model.pkl")

_model = None
_model_load_error = None

def _load_model():
    global _model, _model_load_error
    if _model is not None or _model_load_error is not None:
        return _model
    try:
        _model = joblib.load(MODEL_PATH)
    except Exception as exc:
        _model_load_error = exc
        _model = None
    return _model

def capitalize_contents(data):
    """Recursively uppercase all string leaves in nested dict/list structures."""
    if isinstance(data, dict):
        return {k: capitalize_contents(v) for k, v in data.items()}
    if isinstance(data, list):
        return [capitalize_contents(v) for v in data]
    if isinstance(data, str):
        return data.upper()
    return data

REQUIRED_FEATURE_ORDER = [
    "School Term", "Age at Enrollment", "Requirement Agreement", "Disability", "Indigenous",
    "Program (First Choice)", "Program (Second Choice)", "Entry Level", "Birth City", "Place of Birth (Province)",
    "Gender", "Citizen of", "Religion", "Civil Status", "Current Region", "Current Province", "City/Municipality",
    "Current Brgy.", "Permanent Country", "Permanent Region", "Permanent Province", "Permanent City", "Permanent Brgy.",
    "Birth Country", "Student Type", "School Type"
]

def predict_enrollment_probability(feature_map: Dict[str, Any]) -> float:
    """Return probability (0..1) of enrollment using the Random Forest model.

    feature_map must already contain the REQUIRED_FEATURE_ORDER keys.
    Missing keys fall back to empty string / 0.
    """
    model = _load_model()
    if model is None:
        # Heuristic fallback
        req = feature_map.get("Requirement Agreement", 0)
        program = feature_map.get("Program (First Choice)") or ""
        return 0.65 if (str(req) in {"1","TRUE","YES"} and program) else 0.35

    # Uppercase categorical string values to match expected training normalization
    normalized = {}
    for k in REQUIRED_FEATURE_ORDER:
        v = feature_map.get(k, "")
        if isinstance(v, str):
            normalized[k] = v.upper().strip()
        else:
            normalized[k] = v

    df = pd.DataFrame([[normalized[k] for k in REQUIRED_FEATURE_ORDER]], columns=REQUIRED_FEATURE_ORDER)
    try:
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(df)[0]
            # Assume binary classification; positive class index 1
            if len(proba) >= 2:
                return float(proba[1])
            return float(max(proba))
        # No predict_proba: approximate from prediction
        pred = model.predict(df)[0]
        return 0.7 if int(pred) == 1 else 0.3
    except Exception:
        return 0.5

def predict_enrollment_chance(features_json: str) -> Tuple[str, float]:
    """Compatibility wrapper returning (label, probability)."""
    try:
        feat = json.loads(features_json)
    except Exception:
        feat = {}
    prob = predict_enrollment_probability(feat)
    label = "Likely" if prob >= 0.5 else "Unlikely"
    return label, prob

# Backwards compatibility (if any old imports remain)
def predict_enrollment(features: Any):
    model = _load_model()
    if model is None:
        return 0
    return model.predict([features])[0]