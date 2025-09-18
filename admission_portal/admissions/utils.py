import json
from pathlib import Path
from datetime import date
from .models import Student

# Features as specified
FEATURE_FILE_BASENAME = 'latest_registration_features.json'

def calculate_age_at_enrollment(birth_date):
    if not birth_date:
        return None
    today = date.today()
    try:
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    except Exception:
        return None


def build_flat_record(student: Student):
    # Derive numeric year from school_year
    school_year_recent = None
    if student.school_year and '-' in student.school_year:
        try:
            school_year_recent = int(student.school_year.split('-')[-1])
        except Exception:
            pass
    school_term_numeric = safe_int(str(student.school_term).rstrip('stndrdth')) if student.school_term else None
    age_val = student.age_at_enrollment if student.age_at_enrollment is not None else calculate_age_at_enrollment(student.birth_date)
    # Compose birth place combined format City, Province if available
    birth_place_combo = None
    if student.birth_city or student.birth_province:
        birth_place_combo = ", ".join([p for p in [student.birth_city, student.birth_province] if p])

    status_val = 'ENROLLED' if student.student_id else 'NOT ENROLLED'
    def up(val):
        return val.upper() if isinstance(val, str) else val
    # Normalize specific categorical values to uppercase (as per sample)
    return {
        'ID': student.pk,
        'School Year': school_year_recent or student.school_year,
        'School Term': school_term_numeric,
        'Campus Code': up(student.campus_code),
        'Program (First Choice)': up(student.program_first_choice),
        'Program (Second Choice)': up(student.program_second_choice),
        'Entry Level': up(student.entry_level),
        'Full Name': up(student.full_name),
        'Last Name': up(student.last_name),
        'First Name': up(student.first_name),
        'Suffix': student.suffix or "",
        'Prefix': student.prefix or "",
        'Middle Name': up(student.middle_name),
        'Age at Enrollment': age_val,
        'Birth Date': student.birth_date.isoformat() if student.birth_date else None,
        'Birth Place': birth_place_combo,
        'Birth City': student.birth_city,
        'Place of Birth (Province)': student.birth_province,
        'Gender': up(student.gender),
        'Citizen of': up(student.citizen_of),
        'Religion': student.religion,
        'Civil Status': up(student.civil_status),
        'Current Region': student.current_region,
        'Current Province': student.current_province,
        'City/Municipality': student.current_city,
        'Current Brgy.': student.current_brgy,
        'Current Street': student.current_street,
        'Current Postal Code': safe_int(student.current_postal_code),
        'Permanent Country': up(student.permanent_country),
        'Permanent Region': student.permanent_region,
        'Permanent Province': student.permanent_province,
        'Permanent City': student.permanent_city,
        'Permanent Brgy.': student.permanent_brgy,
        'Permanent Street': student.permanent_street,
        'Permanent Postal Code': safe_int(student.permanent_postal_code),
        'Disability': safe_int(student.disability),
        'Indigenous': safe_int(student.indigenous),
        'Birth Country': up(student.birth_country),
        'Requirement Agreement': safe_int(student.requirement_agreement),
        'Student Type': student.student_type,
        'Last School Attended': student.last_school_attended,
        'School Type': up(student.school_type),
        'Status': status_val,
    }


def safe_int(value):
    try:
        if value in (True, False):
            return int(value)
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        # Accept strings like '1' or '0'; otherwise None
        try:
            return int(str(value))
        except Exception:
            return None


def write_feature_json(student: Student, directory: str | Path | None = None) -> Path:
    """Append or update a flattened student record inside a JSON file under key dummy_Student{pk}."""
    if directory is None:
        directory = Path(__file__).resolve().parent / 'data'
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / FEATURE_FILE_BASENAME

    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            data = {}
    record_key = f"dummy_Student{student.pk}"
    data[record_key] = build_flat_record(student)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path
