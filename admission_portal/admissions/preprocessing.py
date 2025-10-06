"""
Student Enrollment Prediction - Data Preprocessing Module

This module contains preprocessing functions to transform raw student data
into features ready for model prediction, following the same preprocessing
pipeline used during training.

Usage:
    from preprocessing import preprocess_student_data
    
    # For single student
    processed_data = preprocess_student_data(student_dict)
    
    # For batch processing
    processed_df = preprocess_student_data_batch(students_list)
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Faculty mapping for program classification
FACULTY_MAP = {
    # SACE (School of Arts, Computing, and Engineering)
    'BACHELOR OF SCIENCE IN COMPUTER SCIENCE': 'SACE',
    'BACHELOR OF SCIENCE IN ARCHITECTURE': 'SACE',
    'BACHELOR OF SCIENCE IN INFORMATION TECHNOLOGY': 'SACE',
    'BACHELOR OF SCIENCE IN CIVIL ENGINEERING': 'SACE',

    # SAHS (School of Allied Health Sciences)
    'BACHELOR OF SCIENCE IN NURSING': 'SAHS',
    'BACHELOR OF SCIENCE IN MEDICAL TECHNOLOGY': 'SAHS',
    'BACHELOR OF SCIENCE IN PSYCHOLOGY': 'SAHS',

    # SABM (School of Accountancy and Business Management)
    'BACHELOR OF SCIENCE IN ACCOUNTANCY': 'SABM',
    'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN MARKETING MANAGEMENT': 'SABM',
    'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN FINANCIAL MANAGEMENT': 'SABM',
    'BACHELOR OF SCIENCE IN TOURISM MANAGEMENT': 'SABM',
}

# Entry level frequency mapping (from training data)
ENTRY_LEVEL_FREQ = {
    'FRESHMAN': 18673,
    'TRANSFEREE': 1478,
    '2ND_DEGREE': 145,
    'CROSS_ENROLLEE': 41,
    'GRADUATE_STUDIES': 2
}

# Top 20 provinces from training data (you may need to update this based on actual training data)
TOP20_PROVINCES = [
    'BATANGAS', 'LAGUNA', 'CAVITE', 'QUEZON', 'RIZAL', 'MANILA', 'ORIENTAL MINDORO',
    'BULACAN', 'ALBAY', 'CAMARINES SUR', 'MARINDUQUE', 'ROMBLON', 'OCCIDENTAL MINDORO',
    'SORSOGON', 'CAMARINES NORTE', 'CATANDUANES', 'MASBATE', 'TARLAC', 'NUEVA ECIJA',
    'PALAWAN'
]

# Top 20 cities from training data (you may need to update this based on actual training data)
TOP20_CITIES = [
    'LIPA', 'SAN JOSE', 'BATANGAS CITY', 'TANAUAN', 'SANTO TOMAS', 'CALAMBA', 'SAN PABLO',
    'BIÑAN', 'MALVAR', 'BAUAN', 'LEMERY', 'NASUGBU', 'CANDELARIA', 'IBAAN', 'LOBO',
    'SAN LUIS', 'TAYSAN', 'MATAAS NA KAHOY', 'CUENCA', 'AGONCILLO'
]


def normalize_city_names(city_str):
    """Normalize city names by removing 'city of' and 'city' suffixes/prefixes"""
    if pd.isna(city_str) or city_str in ['N/A', 'NA', '', None]:
        return 'N/A'
    
    city_str = str(city_str).strip().lower()
    # Remove "city of " at start
    city_str = pd.Series([city_str]).str.replace(r"^city of\s+", "", regex=True).iloc[0]
    # Remove " city" at end
    city_str = pd.Series([city_str]).str.replace(r"\s+city$", "", regex=True).iloc[0]
    # Replace multiple spaces with single space
    city_str = pd.Series([city_str]).str.replace(r"\s+", " ", regex=True).iloc[0]
    
    return city_str


def normalize_program_name(program_str):
    """Normalize program names to match training data format"""
    if pd.isna(program_str) or program_str in ['N/A', 'NA', '', None]:
        return 'N/A'
    
    # Convert to uppercase and strip
    program_str = str(program_str).strip().upper()
    
    # Remove MLA and MWA suffixes
    program_str = pd.Series([program_str]).str.replace(r"\s*-\s*MLA$", "", regex=True).iloc[0]
    program_str = pd.Series([program_str]).str.replace(r"\s*-\s*MWA$", "", regex=True).iloc[0]
    
    # Handle abbreviation replacements
    abbreviations = {
        'BSN': 'BACHELOR OF SCIENCE IN NURSING',
        'BSCE': 'BACHELOR OF SCIENCE IN CIVIL ENGINEERING',
        'BSMT': 'BACHELOR OF SCIENCE IN MEDICAL TECHNOLOGY',
        'BSPSY': 'BACHELOR OF SCIENCE IN PSYCHOLOGY',
        'BSA': 'BACHELOR OF SCIENCE IN ACCOUNTANCY',
        'BSACCOUNTANCY': 'BACHELOR OF SCIENCE IN ACCOUNTANCY',
        'BSIT': 'BACHELOR OF SCIENCE IN INFORMATION TECHNOLOGY',
        'BSTM': 'BACHELOR OF SCIENCE IN TOURISM MANAGEMENT',
        'BSARCH': 'BACHELOR OF SCIENCE IN ARCHITECTURE',
        'BSBA-MKTGMGT': 'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN MARKETING MANAGEMENT',
        'BSBA-FINMGT': 'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN FINANCIAL MANAGEMENT',
        'BSCS': 'BACHELOR OF SCIENCE IN COMPUTER SCIENCE'
    }
    
    if program_str in abbreviations:
        program_str = abbreviations[program_str]
    
    return program_str


def simplify_civil_status(x):
    """Simplify civil status to main categories"""
    if pd.isna(x) or str(x).strip().upper() in ['N/A', 'NA', '', None]:
        return "OTHER"
    x = str(x).strip().upper()
    if x == "MARRIED":
        return "MARRIED"
    elif x == "SINGLE":
        return "SINGLE"
    else:
        return "OTHER"


def simplify_student_type(x):
    """Convert student type to binary encoding"""
    if pd.isna(x) or str(x).strip().upper() == "N/A":
        return -1
    x = str(x).strip().upper()
    if x == "FULL-TIME STUDENT":
        return 1   # Full-time
    else:
        return 0   # Working student or other


def simplify_school_type(x):
    """Convert school type to binary encoding"""
    if pd.isna(x) or str(x).strip().upper() == "N/A":
        return -1   # Unknown / missing
    x = str(x).strip().upper()
    if x == "PRIVATE":
        return 1
    else:
        return 0   # Public


def preprocess_student_data(student_dict):
    """
    Preprocess a single student's data for model prediction.
    
    Args:
        student_dict (dict): Dictionary containing student information
        
    Returns:
        dict: Processed features ready for model prediction
        
    Example:
        student_data = {
            "School Year": 2025,
            "School Term": 1,
            "Program (First Choice)": "BSN",
            "Program (Second Choice)": "BSPSY",
            "Entry Level": "FRESHMAN",
            "Age at Enrollment": 18,
            "Birth Date": "2007-06-12",
            "Gender": "FEMALE",
            "Civil Status": "SINGLE",
            "Religion": "Roman Catholic",
            "Permanent Province": "Batangas",
            "Permanent City": "Lipa",
            "Disability": 0,
            "Indigenous": 0,
            "Requirement Agreement": 1,
            "Student Type": "Full-time Student",
            "School Type": "PUBLIC"
        }
        processed = preprocess_student_data(student_data)
    """
    
    # Create a copy to avoid modifying original
    data = student_dict.copy()
    
    # === STEP 1: Basic column setup and null handling ===
    
    # Replace null values with N/A initially
    for key, value in data.items():
        if pd.isna(value) or value is None or value == '':
            data[key] = 'N/A'
    
    # === STEP 2: Age calculation ===
    if 'Birth Date' in data and 'School Year' in data:
        if data['Birth Date'] != 'N/A':
            try:
                birth_date = pd.to_datetime(data['Birth Date'])
                data['Age at Enrollment'] = int(data['School Year']) - birth_date.year
            except:
                data['Age at Enrollment'] = 'N/A'
        else:
            data['Age at Enrollment'] = 'N/A'
    
    # === STEP 3: Binary transformations for special fields ===
    
    # Requirement Agreement: 1 if not null/empty, 0 otherwise
    if 'Requirement Agreement' in data:
        data['Requirement Agreement'] = 1 if (data['Requirement Agreement'] not in ['N/A', 'NA', '', None, 0] and pd.notna(data['Requirement Agreement'])) else 0
    else:
        data['Requirement Agreement'] = 0
    
    # Disability: 1 if not null/empty, 0 otherwise
    if 'Disability' in data:
        data['Disability'] = 1 if (data['Disability'] not in ['N/A', 'NA', '', None, 0] and pd.notna(data['Disability'])) else 0
    else:
        data['Disability'] = 0
    
    # Indigenous: 1 if not null/empty, 0 otherwise
    if 'Indigenous' in data:
        data['Indigenous'] = 1 if (data['Indigenous'] not in ['N/A', 'NA', '', None, 0] and pd.notna(data['Indigenous'])) else 0
    else:
        data['Indigenous'] = 0
    
    # === STEP 4: Text normalization ===
    
    # Normalize city names
    city_columns = ['Birth City', 'City/Municipality', 'Permanent City']
    for col in city_columns:
        if col in data:
            data[col] = normalize_city_names(data[col])
    
    # Normalize province names
    province_columns = ['Permanent Province', 'Place of Birth (Province)']
    for col in province_columns:
        if col in data:
            data[col] = normalize_city_names(data[col])  # Same normalization
    
    # Capitalize all string data for consistency (except Age at Enrollment)
    for key, value in data.items():
        if key not in ['Age at Enrollment', 'School Year', 'School Term'] and isinstance(value, str):
            if value != 'N/A':
                data[key] = value.upper()
    
    # === STEP 5: Program normalization ===
    
    # Normalize program names
    if 'Program (First Choice)' in data:
        data['Program (First Choice)'] = normalize_program_name(data['Program (First Choice)'])
    
    if 'Program (Second Choice)' in data:
        data['Program (Second Choice)'] = normalize_program_name(data['Program (Second Choice)'])
        # Replace various null representations with pd.NA for second choice
        if data['Program (Second Choice)'] in ['N/A', 'NA', 'NAN', '', None]:
            data['Program (Second Choice)'] = None
    
    # Remove header-like rows (just in case)
    if 'Program (First Choice)' in data and 'PROGRAM' in str(data['Program (First Choice)']):
        raise ValueError("Invalid program data - appears to be a header row")
    
    # === STEP 6: Advanced Feature Engineering ===
    
    # Faculty mapping
    first_faculty = FACULTY_MAP.get(data.get('Program (First Choice)', ''), 'OTHER')
    second_faculty = FACULTY_MAP.get(data.get('Program (Second Choice)', ''), 'OTHER') if data.get('Program (Second Choice)') else 'OTHER'
    
    data['first_faculty'] = first_faculty
    data['second_faculty'] = second_faculty
    
    # Program choice analysis
    data['second_choice_missing'] = 1 if not data.get('Program (Second Choice)') else 0
    data['same_faculty'] = 1 if (first_faculty == second_faculty and second_faculty != 'OTHER') else 0
    data['valid_second_choice'] = 1 if data.get('Program (Second Choice)') in FACULTY_MAP else 0
    data['second_choice_other'] = 1 if second_faculty == 'OTHER' else 0
    data['diff_faculty'] = 1 if (first_faculty != second_faculty and second_faculty != 'OTHER') else 0
    
    # Entry level processing
    entry_level = data.get('Entry Level', 'FRESHMAN')
    
    # Group small categories
    entry_level_grouped = entry_level
    if entry_level in ['2ND_DEGREE', 'CROSS_ENROLLEE', 'GRADUATE_STUDIES']:
        entry_level_grouped = 'OTHER'
    
    data['Entry Level Grouped'] = entry_level_grouped
    data['is_transferee'] = 1 if entry_level == 'TRANSFEREE' else 0
    data['is_other_entry'] = 1 if entry_level_grouped == 'OTHER' else 0
    data['entry_level_freq'] = ENTRY_LEVEL_FREQ.get(entry_level, 0)
    
    # Geographic grouping
    permanent_province = data.get('Permanent Province', 'N/A')
    data['Permanent Province Grouped'] = permanent_province if permanent_province in TOP20_PROVINCES else 'OTHER'
    
    permanent_city = data.get('Permanent City', 'N/A')
    data['Permanent City Grouped'] = permanent_city if permanent_city in TOP20_CITIES else 'OTHER'
    
    # Demographic features
    data['civil_status_grouped'] = simplify_civil_status(data.get('Civil Status', 'N/A'))
    
    # Religion grouping (majority vs minority)
    religion = data.get('Religion', 'N/A')
    data['religion_grouped'] = 'MAJORITY' if str(religion).strip().upper() == 'ROMAN CATHOLIC' else 'MINORITY'
    
    # Gender binary encoding
    gender = data.get('Gender', 'N/A')
    data['gender_binary'] = 1 if str(gender).strip().upper() == 'FEMALE' else 0
    
    # Student and School type binary encoding
    data['student_type_binary'] = simplify_student_type(data.get('Student Type', 'N/A'))
    data['school_type_binary'] = simplify_school_type(data.get('School Type', 'N/A'))
    
    # === STEP 7: Final feature selection ===
    # Keep only the features that match the training data
    
    final_features = {
        'School Year': data.get('School Year', 2025),
        'School Term': data.get('School Term', 1),
        'Program (First Choice)': data.get('Program (First Choice)', 'N/A'),
        'Program (Second Choice)': data.get('Program (Second Choice)'),  # Can be None
        'Place of Birth (Province)': data.get('Place of Birth (Province)', 'N/A'),
        'Permanent Region': data.get('Permanent Region', 'N/A'),
        'Age at Enrollment': data.get('Age at Enrollment', 'N/A'),
        'Requirement Agreement': data.get('Requirement Agreement', 0),
        'Disability': data.get('Disability', 0),
        'Indigenous': data.get('Indigenous', 0),
        'first_faculty': data['first_faculty'],
        'second_faculty': data['second_faculty'],
        'second_choice_missing': data['second_choice_missing'],
        'same_faculty': data['same_faculty'],
        'valid_second_choice': data['valid_second_choice'],
        'second_choice_other': data['second_choice_other'],
        'diff_faculty': data['diff_faculty'],
        'Entry Level Grouped': data['Entry Level Grouped'],
        'is_transferee': data['is_transferee'],
        'is_other_entry': data['is_other_entry'],
        'entry_level_freq': data['entry_level_freq'],
        'Permanent Province Grouped': data['Permanent Province Grouped'],
        'Permanent City Grouped': data['Permanent City Grouped'],
        'civil_status_grouped': data['civil_status_grouped'],
        'religion_grouped': data['religion_grouped'],
        'gender_binary': data['gender_binary'],
        'student_type_binary': data['student_type_binary'],
        'school_type_binary': data['school_type_binary'],
    }
    
    return final_features


def preprocess_student_data_batch(students_list):
    """
    Preprocess a batch of students' data for model prediction.
    
    Args:
        students_list (list): List of dictionaries containing student information
        
    Returns:
        pd.DataFrame: Processed features ready for model prediction
    """
    processed_students = []
    
    for i, student in enumerate(students_list):
        try:
            processed = preprocess_student_data(student)
            processed_students.append(processed)
        except Exception as e:
            print(f"Error processing student {i}: {e}")
            continue
    
    if not processed_students:
        raise ValueError("No students were successfully processed")
    
    return pd.DataFrame(processed_students)


# Example usage and testing function
def test_preprocessing():
    """Test the preprocessing function with sample data"""
    
    # Sample student data
    test_student = {
        "School Year": 2025,
        "School Term": 1,
        "Program (First Choice)": "BSN",  # Will be normalized to full name
        "Program (Second Choice)": "BSPSY",  # Will be normalized to full name
        "Entry Level": "FRESHMAN",
        "Age at Enrollment": 18,
        "Birth Date": "2007-06-12",
        "Place of Birth (Province)": "Batangas",
        "Gender": "FEMALE",
        "Civil Status": "SINGLE",
        "Religion": "Roman Catholic",
        "Permanent Region": "Region IV-A",
        "Permanent Province": "Batangas",
        "Permanent City": "Lipa",
        "Disability": 0,
        "Indigenous": 0,
        "Requirement Agreement": 1,
        "Student Type": "Full-time Student",
        "School Type": "PUBLIC"
    }
    
    print("=== Testing Preprocessing Function ===")
    print("Original data:")
    for key, value in test_student.items():
        print(f"  {key}: {value}")
    
    processed = preprocess_student_data(test_student)
    
    print("\nProcessed data:")
    for key, value in processed.items():
        print(f"  {key}: {value}")
    
    print(f"\nTotal features: {len(processed)}")
    
    return processed


if __name__ == "__main__":
    test_preprocessing()