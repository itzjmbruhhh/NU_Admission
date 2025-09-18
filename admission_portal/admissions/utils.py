import json
from pathlib import Path
from datetime import datetime, date
from .models import Student

FEATURE_FILE_BASENAME = 'latest_registration_features.json'


def calculate_age_at_enrollment(birth_date):
    """Compute age in years from birth_date (datetime.date or string YYYY-MM-DD)."""
    if not birth_date:
        return None
    if isinstance(birth_date, str):
        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            return None
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def safe_int(value):
    """Convert a value to int, handle None, bool, or string representations."""
    try:
        if value in (True, False):
            return int(value)
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(str(value))
        except Exception:
            return None


def safe_date(value):
    """Convert date-like value to ISO string YYYY-MM-DD."""
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, str):
        try:
            dt = datetime.strptime(value, "%Y-%m-%d")
            return dt.date().isoformat()
        except Exception:
            return value  # fallback: keep original string
    return str(value)


def build_flat_record(student: Student):
    """Flatten a Student instance into a dictionary suitable for ML features."""
    def up(val):
        return val.upper().strip() if isinstance(val, str) else val

    # Numeric fields
    school_term_numeric = safe_int(str(student.school_term).rstrip('stndrdth')) if student.school_term else None
    age_val = student.age_at_enrollment if student.age_at_enrollment is not None else calculate_age_at_enrollment(student.birth_date)
    school_year_recent = None
    if student.school_year and '-' in student.school_year:
        try:
            school_year_recent = int(student.school_year.split('-')[-1])
        except Exception:
            school_year_recent = None

    # Compose birth place combined format City, Province
    birth_place_combo = ", ".join([p for p in [student.birth_city, student.birth_province] if p]) if (student.birth_city or student.birth_province) else None

    # Status
    status_val = 'ENROLLED' if student.student_id else 'NOT ENROLLED'

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
        'Birth Date': safe_date(student.birth_date),
        'Birth Place': birth_place_combo,
        'Birth City': student.birth_city or "",
        'Place of Birth (Province)': student.birth_province or "",
        'Gender': up(student.gender),
        'Citizen of': up(student.citizen_of),
        'Religion': student.religion or "",
        'Civil Status': up(student.civil_status),
        'Current Region': student.current_region or "",
        'Current Province': student.current_province or "",
        'City/Municipality': student.current_city or "",
        'Current Brgy.': student.current_brgy or "",
        'Current Street': student.current_street or "",
        'Current Postal Code': safe_int(student.current_postal_code),
        'Permanent Country': up(student.permanent_country),
        'Permanent Region': student.permanent_region or "",
        'Permanent Province': student.permanent_province or "",
        'Permanent City': student.permanent_city or "",
        'Permanent Brgy.': student.permanent_brgy or "",
        'Permanent Street': student.permanent_street or "",
        'Permanent Postal Code': safe_int(student.permanent_postal_code),
        'Disability': safe_int(student.disability),
        'Indigenous': safe_int(student.indigenous),
        'Birth Country': up(student.birth_country),
        'Requirement Agreement': safe_int(student.requirement_agreement),
        'Student Type': student.student_type or "",
        'Last School Attended': student.last_school_attended or "",
        'School Type': up(student.school_type),
        'Status': status_val,
    }


def write_feature_json(student: Student, directory: str | Path | None = None) -> Path:
    """Save or update a flattened student record inside a JSON file."""
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
