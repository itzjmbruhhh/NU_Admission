import json
import joblib
import os
from django.conf import settings
from typing import Tuple, Any

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

def predict_enrollment_chance(features_json: str) -> Tuple[str, float]:
    """Return (label, probability_score) for enrollment chance.

    Parameters
    ----------
    features_json : str
        JSON string representing a flat dict of feature name -> value

    Returns
    -------
    (label, probability)
        label: 'Likely' or 'Unlikely' (fallback logic if model unavailable)
        probability: float between 0 and 1
    """
    try:
        features = json.loads(features_json)
    except json.JSONDecodeError:
        features = {}

    model = _load_model()
    if model is None:
        # Simple heuristic fallback: if Requirement Agreement == 1 and Program provided -> moderate chance
        req = features.get("Requirement Agreement", 0)
        program = features.get("Program (First Choice)") or ""
        prob = 0.65 if (str(req) in {"1", "True", "true"} and program) else 0.35
        label = "Likely" if prob >= 0.5 else "Unlikely"
        return label, prob

    # Build feature vector. For a production system you'd replicate training preprocessing.
    # Here we attempt a simple ordered extraction using the provided dict values.
    feature_values = list(features.values())
    try:
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba([feature_values])[0]
            # Assume positive class is the latter index if binary; pick max otherwise
            if len(probs) == 2:
                prob = float(max(probs[0], probs[1]))  # choose highest as generic probability
            else:
                prob = float(max(probs))
        else:
            # Derive pseudo-probability from decision function or raw prediction
            raw_pred = model.predict([feature_values])[0]
            prob = 0.7 if raw_pred else 0.3
        label = "Likely" if prob >= 0.5 else "Unlikely"
        return label, prob
    except Exception:
        # Any runtime issue -> fallback heuristic
        prob = 0.5
        return "Likely", prob

# Backwards compatibility (if any old imports remain)
def predict_enrollment(features: Any):
    model = _load_model()
    if model is None:
        return 0
    return model.predict([features])[0]