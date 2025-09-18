from django.shortcuts import get_object_or_404
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_detail.html', {'student': student})
# admissions/views.py
from django.shortcuts import render, redirect
from .models import Student
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from .models  import Student


def index(request):
    return render(request, 'index.html')

def loginAdmin(request):
    return render(request, 'login.html')

def adminDash(request):
    # Admission success rate (enrolled vs not enrolled)
    admission_labels = ["Enrolled", "Not Enrolled"]
    admission_data = [
        Student.objects.exclude(student_id__isnull=True).exclude(student_id__exact='').count(),
        Student.objects.filter(student_id__isnull=True).count() + Student.objects.filter(student_id__exact='').count()
    ]
    # --- Male/Female enrolled counts and percentages ---
    enrolled_students = Student.objects.exclude(student_id__isnull=True).exclude(student_id__exact='')
    male_enrolled_count = enrolled_students.filter(gender__iexact='Male').count()
    female_enrolled_count = enrolled_students.filter(gender__iexact='Female').count()
    total_enrolled = male_enrolled_count + female_enrolled_count
    if total_enrolled > 0:
        male_enrolled_percent = (male_enrolled_count / total_enrolled) * 100
        female_enrolled_percent = (female_enrolled_count / total_enrolled) * 100
    else:
        male_enrolled_percent = 0
        female_enrolled_percent = 0
    from datetime import date
    student_id = request.GET.get('student_id')
    programs = Student.objects.values_list('program_first_choice', flat=True).distinct()
    school_years = Student.objects.values_list('school_year', flat=True).distinct()
    statuses = ['Enrolled', 'Not Enrolled']
    program = request.GET.get('program')
    school_year = request.GET.get('school_year')
    status = request.GET.get('status')

    students = Student.objects.all().order_by('-school_year', '-school_term')
    if program:
        students = students.filter(program_first_choice=program)
    if school_year:
        students = students.filter(school_year=school_year)
    if status == 'Enrolled':
        students = students.exclude(student_id__isnull=True).exclude(student_id__exact='')
    elif status == 'Not Enrolled':
        students = students.filter(student_id__isnull=True) | students.filter(student_id__exact='')
    if student_id:
        students = students.filter(student_id__icontains=student_id)

    # Pagination
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    students_page = paginator.get_page(page_number)

    # --- Dashboard summary logic ---
    # Get current year/term (assume latest school_year and school_term in DB)
    latest_student = Student.objects.order_by('-school_year', '-school_term').first()
    current_year = latest_student.school_year if latest_student else None
    current_term = latest_student.school_term if latest_student else None

    # Get enrolled counts per school year for current term
    enrolled_qs = Student.objects.filter(
        school_term=current_term
    ).exclude(student_id__isnull=True).exclude(student_id__exact='')
    # Get counts per year, sorted
    from collections import OrderedDict
    enrolled_counts = {}
    for y in school_years:
        count = enrolled_qs.filter(school_year=y).count()
        enrolled_counts[str(y)] = count
    # Sort by year
    enrolled_counts = OrderedDict(sorted(enrolled_counts.items(), key=lambda x: x[0]))
    # Get current and previous year counts
    current_enrolled_count = enrolled_counts.get(str(current_year), 0)
    years_sorted = list(enrolled_counts.keys())
    if len(years_sorted) > 1:
        idx = years_sorted.index(str(current_year))
        if idx > 0:
            last_year = years_sorted[idx-1]
            last_enrolled_count = enrolled_counts[last_year]
            if last_enrolled_count:
                percent_change = ((current_enrolled_count - last_enrolled_count) / last_enrolled_count) * 100
            else:
                percent_change = 0
        else:
            percent_change = 0
    else:
        percent_change = 0

    # --- Top Program among enrolled students ---
    from django.db.models import Count
    top_program_data = (
        enrolled_students.values('program_first_choice')
        .annotate(count=Count('program_first_choice'))
        .order_by('-count')
        .first()
    )
    top_program = top_program_data['program_first_choice'] if top_program_data else None
    top_program_count = top_program_data['count'] if top_program_data else 0

    # Academic year distribution for enrolled students
    academic_year_labels = list(enrolled_counts.keys())
    academic_year_data = list(enrolled_counts.values())

    # Program popularity for pie chart
    program_popularity = (
        enrolled_students.values('program_first_choice')
        .annotate(count=Count('program_first_choice'))
        .order_by('-count')
    )
    program_labels = [p['program_first_choice'] for p in program_popularity]
    program_data = [p['count'] for p in program_popularity]

    context = {
        'students': students_page,
        'programs': programs,
        'statuses': statuses,
        'school_years': school_years,
        'selected_program': program,
        'selected_status': status,
        'selected_school_year': school_year,
        'current_enrolled_count': current_enrolled_count,
        'current_year': current_year,
        'current_term': current_term,
        'percent_change': percent_change,
        'male_enrolled_count': male_enrolled_count,
        'female_enrolled_count': female_enrolled_count,
        'male_enrolled_percent': male_enrolled_percent,
        'female_enrolled_percent': female_enrolled_percent,
        'top_program': top_program,
        'top_program_count': top_program_count,
        'academic_year_labels': academic_year_labels,
        'academic_year_data': academic_year_data,
        'program_labels': program_labels,
        'program_data': program_data,
        'admission_labels': admission_labels,
        'admission_data': admission_data,
    }
    return render(request, 'admin.html', context)

def register(request):
    return render(request, 'registration.html')

def register_student(request):
    if request.method == "POST":
        import json
        import tempfile
        from .ml_utils import predict_enrollment_chance

        form = request.POST
        # --- Feature extraction ---
        school_term = form.get("schoolTerm")
        age_at_enrollment = form.get("ageAtEnrollment") or ""
        requirement_agreement = form.get("truthfulInfo", "No")
        disability = form.get("disability", "No")
        indigenous = form.get("indigenous", "No")
        program_first_choice = form.get("firstChoice", "")
        program_second_choice = form.get("secondChoice", "")
        entry_level = form.get("entryLevel", "")
        birth_city = form.get("birthCity", "")
        birth_province = form.get("birthProvince", "")
        gender = form.get("gender", "")
        citizen_of = form.get("nationality", "")
        religion = form.get("religion", "")
        civil_status = form.get("civilStatus", "")
        current_region = form.get("presentRegion", "")
        current_province = form.get("presentProvince", "")
        current_city = form.get("presentCity", "")
        current_brgy = form.get("presentBarangay", "")
        permanent_country = form.get("permanentCountry", "")
        permanent_region = form.get("permanentRegion", "")
        permanent_province = form.get("permanentProvince", "")
        permanent_city = form.get("permanentCity", "")
        permanent_brgy = form.get("permanentBarangay", "")
        birth_country = form.get("birthCountry", "")
        student_type = form.get("studentType", "")
        school_type = form.get("schoolType", "")

        def bin_convert(val):
            return 1 if str(val).strip().lower() == "yes" else 0
        requirement_agreement_bin = bin_convert(requirement_agreement)
        disability_bin = bin_convert(disability)
        indigenous_bin = bin_convert(indigenous)

        def cap(val):
            return str(val).strip().upper()
        cat_fields = [program_first_choice, program_second_choice, entry_level, birth_city, birth_province, gender,
                     citizen_of, religion, civil_status, current_region, current_province, current_city, current_brgy,
                     permanent_country, permanent_region, permanent_province, permanent_city, permanent_brgy,
                     birth_country, student_type, school_type]
        cat_fields_cap = [cap(f) for f in cat_fields]

        feature_names = [
            "School Term", "Age at Enrollment", "Requirement Agreement", "Disability", "Indigenous",
            "Program (First Choice)", "Program (Second Choice)", "Entry Level", "Birth City", "Place of Birth (Province)",
            "Gender", "Citizen of", "Religion", "Civil Status", "Current Region", "Current Province", "City/Municipality",
            "Current Brgy.", "Permanent Country", "Permanent Region", "Permanent Province", "Permanent City", "Permanent Brgy.",
            "Birth Country", "Student Type", "School Type"
        ]
        feature_values = [school_term, age_at_enrollment, requirement_agreement_bin, disability_bin, indigenous_bin] + cat_fields_cap
        features = dict(zip(feature_names, feature_values))

        # --- Create temporary JSON file ---
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_json:
            json.dump(features, tmp_json)
            tmp_json_path = tmp_json.name

        # --- Predict ---
        features_json = json.dumps(features)
        pred_label, pred_prob = predict_enrollment_chance(features_json)

        # --- Save to DB ---
        student = Student.objects.create(
            school_year=form.get("schoolYear"),
            school_term=school_term,
            campus_code=form.get("campus"),
            program_first_choice=program_first_choice,
            program_second_choice=program_second_choice,
            entry_level=entry_level,
            first_name=form.get("firstName"),
            middle_name=form.get("middleName"),
            last_name=form.get("lastName"),
            suffix=form.get("suffix"),
            gender=gender,
            civil_status=civil_status,
            birth_date=form.get("birthDate"),
            birth_place=form.get("birthPlace"),
            birth_city=birth_city,
            birth_province=birth_province,
            birth_country=birth_country,
            citizen_of=citizen_of,
            religion=religion,
            complete_present_address=form.get("presentAddress"),
            current_region=current_region,
            current_province=current_province,
            current_city=current_city,
            current_brgy=current_brgy,
            current_postal_code=form.get("presentZip"),
            permanent_country=permanent_country,
            permanent_region=permanent_region,
            permanent_province=permanent_province,
            permanent_city=permanent_city,
            permanent_brgy=permanent_brgy,
            permanent_postal_code=form.get("permanentZip"),
            email=form.get("emailAddress"),
            mobile_number=form.get("mobileNumber"),
            student_type=student_type,
            school_type=school_type,
            last_school_attended=form.get("lastSchoolAttended", ""),
            requirement_agreement=requirement_agreement_bin,
            disability=disability_bin,
            indigenous=indigenous_bin,
            enrollment_chance=pred_prob
        )
        student.save()
        # Render a result page with prediction
        return render(request, "registration_result.html", {
            "student": student,
            "pred_label": pred_label,
            "pred_prob": pred_prob
        })

    return render(request, "registration.html")