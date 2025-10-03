import pandas as pd
import joblib
import os
import logging
from django.conf import settings
from typing import Dict, Any
from .models import Student
from .preprocessing import preprocess_student_data
import numpy as np

logger = logging.getLogger(__name__)

_model = None
_model_load_error = None
_last_prediction_error: Exception | None = None

"""NOTE: Old REQUIRED_FEATURE_ORDER kept for reference; superseded by training model columns.
The new pipeline relies on `preprocess_student_data` which already produces engineered features.
We will align to whatever columns the loaded model expects (if it has feature_names_in_ or we persist schema).
"""

REQUIRED_FEATURE_ORDER = []  # Deprecated path; kept to avoid breaking imports elsewhere


def _student_to_preprocessing_dict(student: Student) -> dict:
    """Map a Student instance into the raw dict expected by preprocess_student_data.

    The keys must match those documented in preprocessing.py
    (e.g., 'School Year', 'School Term', 'Program (First Choice)', etc.).
    We intentionally leave out engineered fields; preprocess_student_data will derive them.
    """
    # Birth Date: ensure ISO string
    birth_date = None
    if student.birth_date:
        try:
            birth_date = student.birth_date.isoformat()
        except Exception:
            birth_date = str(student.birth_date)

    # Requirement Agreement already stored as truthy string or bool; convert to 1/0 expectation handled inside preprocess.
    # Normalize school term (e.g., '1st','2nd','3rd' -> 1/2/3)
    term_raw = student.school_term or 1
    if isinstance(term_raw, str):
        import re
        m = re.search(r"(\d+)", term_raw)
        term_raw = int(m.group(1)) if m else 1
    # Normalize school year (store recent numeric if range provided)
    sy_raw = student.school_year or "N/A"
    if isinstance(sy_raw, str) and '-' in sy_raw:
        try:
            sy_raw = int(sy_raw.split('-')[-1])
        except Exception:
            pass
    return {
        "School Year": sy_raw,
        "School Term": term_raw,
        "Program (First Choice)": student.program_first_choice or "N/A",
        "Program (Second Choice)": student.program_second_choice or None,
        "Entry Level": (student.entry_level or "FRESHMAN").upper(),
        "Age at Enrollment": student.age_at_enrollment,
        "Birth Date": birth_date,
        "Gender": student.gender or "N/A",
        "Civil Status": student.civil_status or "N/A",
        "Religion": student.religion or "N/A",
        "Permanent Province": student.permanent_province or "N/A",
        "Permanent City": student.permanent_city or "N/A",
        "Place of Birth (Province)": student.birth_province or student.birth_place or "N/A",
        "Birth City": student.birth_city or "N/A",
        "Disability": student.disability or 0,
        "Indigenous": student.indigenous or 0,
        "Requirement Agreement": student.requirement_agreement or 0,
        "Student Type": student.student_type or "N/A",
        "School Type": student.school_type or "N/A",
        # Optional / rarely used keys (can be added if needed by future preprocessing changes)
        "Permanent Region": student.permanent_region or "N/A",
        "Permanent Country": student.permanent_country or "N/A",
    }

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

def predict_student_rf(student_or_profile: Dict[str, Any] | Student) -> Dict[str, Any]:
    """Predict class and probability for either:
    1. A Django Student instance (preferred path), or
    2. A raw dict with Student-like fields (legacy path).

    New logic:
      * Build raw student dictionary -> preprocess_student_data -> engineered feature dict
      * Align columns to model expectations (feature_names_in_ if present) filling missing with NaN
      * Predict probability of positive class (assumed class '1' or second column index)
    """
    model = _load_model()
    if model is None:
        return {"Prediction": 0, "Probability": 0.5}

    # Step 1: derive raw student dict appropriate for preprocessing
    if isinstance(student_or_profile, Student):
        raw_dict = _student_to_preprocessing_dict(student_or_profile)
    else:
        raw_dict = student_or_profile

    # Step 2: preprocess to engineered features
    try:
        engineered = preprocess_student_data(raw_dict)
    except Exception as exc:
        logger.exception("Preprocessing failed; fallback: %s", exc)
        return {"Prediction": 0, "Probability": 0.5}

    # Step 3: Build DataFrame
    df = pd.DataFrame([engineered])

    # Step 3b: Coerce numeric columns (avoid strings like 'N/A' or '2nd')
    numeric_cols = [
        'School Year','School Term','Age at Enrollment','Requirement Agreement','Disability','Indigenous',
        'second_choice_missing','same_faculty','valid_second_choice','second_choice_other','diff_faculty',
        'is_transferee','is_other_entry','entry_level_freq','gender_binary','student_type_binary','school_type_binary'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .replace(['N/A','NA','', None], np.nan)
                .apply(lambda v: pd.to_numeric(v, errors='coerce'))
            )

    # Step 4: Align to model columns if available
    try:
        if hasattr(model, 'feature_names_in_'):
            needed_cols = list(model.feature_names_in_)
            df = df.reindex(columns=needed_cols, fill_value=np.nan)
        else:
            # If model is a pipeline, attempt to access underlying estimator
            inner = getattr(model, 'named_steps', {}).get('rf') if hasattr(model, 'named_steps') else None
            if inner is not None and hasattr(inner, 'feature_names_in_'):
                needed_cols = list(inner.feature_names_in_)
                df = df.reindex(columns=needed_cols, fill_value=np.nan)
    except Exception as exc:
        logger.warning("Could not align columns to model schema: %s", exc)

    # Step 5: Predict
    global _last_prediction_error
    try:
        if hasattr(model, 'predict_proba'):
            proba_arr = model.predict_proba(df)
            # Assume positive class is the one with greater label value (common for 0/1)
            if hasattr(model, 'classes_'):
                classes = list(model.classes_)
                # Attempt to find index of class 1 or 'ENROLLED'
                pos_idx = None
                for candidate in [1, 'ENROLLED', 'Yes', 'TRUE', True]:
                    if candidate in classes:
                        pos_idx = classes.index(candidate)
                        break
                if pos_idx is None:
                    # fallback: last column
                    pos_idx = len(classes) - 1
            else:
                pos_idx = 1 if proba_arr.shape[1] > 1 else 0
            pos_proba = float(proba_arr[0][pos_idx])
            pred_class = int(pos_proba >= 0.5)
            return {"Prediction": pred_class, "Probability": pos_proba}
        else:
            pred = model.predict(df)[0]
            # Fallback probability heuristic
            prob = 0.7 if int(pred) == 1 else 0.3
            return {"Prediction": int(pred), "Probability": prob}
    except Exception as exc:
        _last_prediction_error = exc
        logger.exception("Prediction failed; returning fallback: %s", exc)
        return {"Prediction": 0, "Probability": 0.5}

def compute_and_save_enrollment_chance(student: Student) -> float:
    """Compute enrollment probability using new preprocessing pipeline and persist percentage."""
    try:
        pred_dict = predict_student_rf(student)
        student.enrollment_chance = float(pred_dict["Probability"]) * 100.0
        student.save(update_fields=["enrollment_chance"])
        return student.enrollment_chance
    except Exception as exc:
        logger.exception("Failed to compute enrollment chance for student %s: %s", student.id, exc)
        return student.enrollment_chance if student.enrollment_chance is not None else 50.0
