from django.shortcuts import get_object_or_404
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'student_detail.html', {'student': student})
# admissions/views.py
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Student
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from .models  import Student
from .utils import write_feature_json
from .ml_utils import compute_and_save_enrollment_chance


def index(request):
    return render(request, 'index.html')

def loginAdmin(request):
    return render(request, 'login.html')

def adminDash(request):
    # Base queryset of enrolled students (student_id present & non-empty)
    enrolled_students = Student.objects.exclude(student_id__isnull=True).exclude(student_id__exact='')

    # Derive list of school years that have at least one enrolled student
    years_with_enrollment_raw = enrolled_students.values_list('school_year', flat=True).distinct()
    # Filter out null/blank and coerce to ints where possible
    years_with_enrollment: list[int] = []
    for y in years_with_enrollment_raw:
        if y is None:
            continue
        y_str = str(y).strip()
        if not y_str:
            continue
        try:
            years_with_enrollment.append(int(y_str))
        except ValueError:
            # Ignore non-numeric year values
            continue
    years_with_enrollment = sorted(set(years_with_enrollment))

    # Guard: if no enrolled years yet, fall back to original broad logic
    if years_with_enrollment:
        min_year = years_with_enrollment[0]
        max_year = years_with_enrollment[-1]
    else:
        min_year = max_year = None

    # Latest enrolled student for current year/term context
    latest_enrolled_student = enrolled_students.order_by('-school_year', '-school_term').first()
    current_year = latest_enrolled_student.school_year if latest_enrolled_student else None
    current_term = latest_enrolled_student.school_term if latest_enrolled_student else None

    # Male / Female counts restricted to currently enrolled population
    male_enrolled_count = enrolled_students.filter(gender__iexact='Male').count()
    female_enrolled_count = enrolled_students.filter(gender__iexact='Female').count()
    total_enrolled = male_enrolled_count + female_enrolled_count
    if total_enrolled > 0:
        male_enrolled_percent = (male_enrolled_count / total_enrolled) * 100
        female_enrolled_percent = (female_enrolled_count / total_enrolled) * 100
    else:
        male_enrolled_percent = female_enrolled_percent = 0
    from datetime import date
    student_id = request.GET.get('student_id')
    programs = Student.objects.values_list('program_first_choice', flat=True).distinct()
    school_years = Student.objects.values_list('school_year', flat=True).distinct()
    statuses = ['Enrolled', 'Not Enrolled']
    program = request.GET.get('program')
    school_year = request.GET.get('school_year')
    status = request.GET.get('status')
    enroll_chance_from = request.GET.get('enroll_chance_from')
    enroll_chance_to = request.GET.get('enroll_chance_to')
    student_type = request.GET.get('student_type')

    # Order by latest registration (most recent first)
    students = Student.objects.all().order_by('-id')
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

    # Enrollment chance range filter
    if enroll_chance_from and enroll_chance_to:
        try:
            from_val = float(enroll_chance_from)
            to_val = float(enroll_chance_to)
            if to_val >= from_val:
                students = students.filter(enrollment_chance__gte=from_val, enrollment_chance__lte=to_val)
        except ValueError:
            pass

    # ✅ Filter by student type
    if student_type:
        students = students.filter(student_type=student_type)

   # Pagination
    paginator = Paginator(students, 10)
    page_number = request.GET.get('page')
    students_page = paginator.get_page(page_number)
    
    # --- Dashboard summary & academic year distribution logic ---
    from collections import OrderedDict
    enrolled_counts = OrderedDict()

    if current_term is not None and min_year is not None and max_year is not None:
        # Restrict to the contiguous numeric range from min_year to max_year
        term_filtered = enrolled_students.filter(school_term=current_term)
        for y in range(min_year, max_year + 1):
            count = term_filtered.filter(school_year=str(y)).count()
            enrolled_counts[str(y)] = count
    else:
        # Fallback: no enrolled students yet. Provide empty counts keyed by distinct school_years.
        for y in school_years:
            enrolled_counts[str(y)] = 0

    current_enrolled_count = enrolled_counts.get(str(current_year), 0) if current_year else 0
    years_sorted = list(enrolled_counts.keys())
    if current_year and str(current_year) in years_sorted:
        idx = years_sorted.index(str(current_year))
        if idx > 0:
            prev_year_key = years_sorted[idx - 1]
            prev_val = enrolled_counts.get(prev_year_key, 0)
            percent_change = ((current_enrolled_count - prev_val) / prev_val * 100) if prev_val else 0
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
    # Abbreviation for top program (reuse mapping) for summary card display
    PROGRAM_ABBREVIATIONS_CARD = {
        'BACHELOR OF SCIENCE IN NURSING': 'BSN',
        'BACHELOR OF SCIENCE IN CIVIL ENGINEERING': 'BSCE',
        'BACHELOR OF SCIENCE IN MEDICAL TECHNOLOGY': 'BSMT',
        'BACHELOR OF SCIENCE IN PSYCHOLOGY': 'BSPSY',
        'BACHELOR OF SCIENCE IN ACCOUNTANCY': 'BSA',
        'BACHELOR OF SCIENCE IN INFORMATION TECHNOLOGY': 'BSIT',
        'BACHELOR OF SCIENCE IN TOURISM MANAGEMENT': 'BSTM',
        'BACHELOR OF SCIENCE IN ARCHITECTURE': 'BSARCH',
        'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN MARKETING MANAGEMENT': 'BSBA-MKTGMGT',
        'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN FINANCIAL MANAGEMENT': 'BSBA-FINMGT',
        'BACHELOR OF SCIENCE IN COMPUTER SCIENCE': 'BSCS',
    }
    top_program_abbrev = None
    if top_program:
        top_program_upper = (top_program or '').strip().upper()
        top_program_abbrev = PROGRAM_ABBREVIATIONS_CARD.get(top_program_upper, top_program)

    # Academic year distribution (already ordered)
    academic_year_labels = list(enrolled_counts.keys())
    academic_year_data = list(enrolled_counts.values())

    # Program popularity for pie chart (based on all currently enrolled students)
    program_popularity = (
        enrolled_students.values('program_first_choice')
        .annotate(count=Count('program_first_choice'))
        .order_by('-count')
    )
    # Map full program names to abbreviations for graph labels
    PROGRAM_ABBREVIATIONS = {
        'BACHELOR OF SCIENCE IN NURSING': 'BSN',
        'BACHELOR OF SCIENCE IN CIVIL ENGINEERING': 'BSCE',
        'BACHELOR OF SCIENCE IN MEDICAL TECHNOLOGY': 'BSMT',
        'BACHELOR OF SCIENCE IN PSYCHOLOGY': 'BSPSY',
        'BACHELOR OF SCIENCE IN ACCOUNTANCY': 'BSA',
        'BACHELOR OF SCIENCE IN INFORMATION TECHNOLOGY': 'BSIT',
        'BACHELOR OF SCIENCE IN TOURISM MANAGEMENT': 'BSTM',
        'BACHELOR OF SCIENCE IN ARCHITECTURE': 'BSARCH',
        'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN MARKETING MANAGEMENT': 'BSBA-MKTGMGT',
        'BACHELOR OF SCIENCE IN BUSINESS ADMINISTRATION MAJOR IN FINANCIAL MANAGEMENT': 'BSBA-FINMGT',
        'BACHELOR OF SCIENCE IN COMPUTER SCIENCE': 'BSCS',
    }
    program_labels = [
        PROGRAM_ABBREVIATIONS.get((p['program_first_choice'] or '').strip().upper(), p['program_first_choice'])
        for p in program_popularity
    ]
    program_data = [p['count'] for p in program_popularity]

    # Admission success rate using entire database (all years)
    total_enrolled_all_years = Student.objects.exclude(student_id__isnull=True).exclude(student_id__exact='').count()
    total_not_enrolled_all_years = Student.objects.filter(Q(student_id__isnull=True) | Q(student_id__exact='')).count()
    admission_labels = ["Enrolled", "Not Enrolled"]
    admission_data = [total_enrolled_all_years, total_not_enrolled_all_years]

    context = {
        'students': students_page,
        'programs': programs,
        'statuses': statuses,
        'school_years': school_years,
        'selected_program': program,
        'selected_status': status,
        'selected_school_year': school_year,
        'selected_enroll_chance': enroll_chance_from,
        'selected_enroll_chance': enroll_chance_to,
        'selected_student_type': student_type,
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
        'top_program_abbrev': top_program_abbrev,
        'academic_year_labels': academic_year_labels,
        'academic_year_data': academic_year_data,
        'program_labels': program_labels,
        'program_data': program_data,
        'admission_labels': admission_labels,
        'admission_data': admission_data,
            'enrollment_chance_counts': [
                Student.objects.filter(enrollment_chance__lt=40).count(),
                Student.objects.filter(enrollment_chance__gte=40, enrollment_chance__lt=70).count(),
                Student.objects.filter(enrollment_chance__gte=70, enrollment_chance__lt=90).count(),
                Student.objects.filter(enrollment_chance__gte=90).count(),
            ],
    }
    return render(request, 'admin.html', context)


def register_student(request):
    if request.method == "POST":
        from datetime import date
        form = request.POST
        school_term = form.get("schoolTerm")
        program_first_choice = form.get("firstChoice", "")
        program_second_choice = form.get("secondChoice", "")
        entry_level = form.get("entryLevel", "")
        birth_city = form.get("birthCity", "")
        birth_province = form.get("birthProvince", "")
        gender = form.get("gender", "")
        citizen_of = form.get("nationality", "")
        religion = form.get("religion", "")
        civil_status = form.get("civilStatus", "")
        current_region = form.get("currentRegion", "") or ""
        current_province = form.get("presentProvince", "")
        current_city = form.get("presentCity", "")
        current_brgy = form.get("presentBarangay", "")
        permanent_country = form.get("permanentCountry", "")
        permanent_region = form.get("permanentRegion", "") or ""
        permanent_province = form.get("permanentProvince", "")
        permanent_city = form.get("permanentCity", "")
        permanent_brgy = form.get("permanentBarangay", "")

        # Fallback: if permanent address fields empty, copy from current
        if not permanent_region:
            permanent_region = current_region
        if not permanent_province:
            permanent_province = current_province
        if not permanent_city:
            permanent_city = current_city
        if not permanent_brgy:
            permanent_brgy = current_brgy
        birth_country = form.get("birthCountry", "")
        student_type = form.get("studentType", "")
        school_type = form.get("schoolType", "")
        requirement_agreement_bin = 1 if form.get("truthfulInfo") else 0
        disability_bin = 1 if form.get("disability", "").strip() else 0
        indigenous_bin = 1 if form.get("indigenous", "").strip() else 0

        # --- Save to DB (prediction removed) ---
        # Compute age at enrollment
        birth_date_str = form.get("birthDate")
        age_at_enrollment = None
        if birth_date_str:
            try:
                year, month, day = map(int, birth_date_str.split('-'))
                bdt = date(year, month, day)
                today = date.today()
                age_at_enrollment = today.year - bdt.year - ((today.month, today.day) < (bdt.month, bdt.day))
            except Exception:
                age_at_enrollment = None

        school_year_val = form.get("schoolYear")
        # Extract the latest year from a range like "2024-2025" (store "2025")
        derived_recent_year = None
        if school_year_val:
            try:
                parts = str(school_year_val).split('-')
                if len(parts) >= 2:
                    derived_recent_year = int(parts[-1])
                else:
                    derived_recent_year = int(parts[0])
            except Exception:
                derived_recent_year = None

        student = Student.objects.create(
            # Store only the latest year (e.g., 2025) in school_year
            school_year=str(derived_recent_year) if derived_recent_year is not None else school_year_val,
            # Keep the submitted term (1st/2nd/3rd)
            school_term=school_term,
            campus_code=form.get("campus"),
            program_first_choice=program_first_choice,
            program_second_choice=program_second_choice,
            entry_level=entry_level,
            full_name=f"{form.get('lastName','').upper()}, {form.get('firstName','').upper()} {form.get('middleName','').upper()}".strip(),
            first_name=form.get("firstName"),
            middle_name=form.get("middleName"),
            last_name=form.get("lastName"),
            suffix=form.get("suffix"),
            gender=gender,
            civil_status=civil_status,
            birth_date=form.get("birthDate"),
            # Form doesn't have distinct birthPlace text input; use province label as birth_place
            birth_place=birth_province,
            birth_city=birth_city,
            birth_province=birth_province,
            birth_country=birth_country,
            citizen_of=citizen_of,
            religion=religion,
            complete_present_address=form.get("presentAddress"),
            current_street=form.get("presentAddress"),
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
            permanent_street=form.get("permanentAddress") or form.get("presentAddress"),
            permanent_postal_code=form.get("permanentZip"),
            email=form.get("emailAddress"),
            mobile_number=form.get("mobileNumber"),
            student_type=student_type,
            school_type=school_type,
            last_school_attended=form.get("lastSchoolAttended", ""),
            requirement_agreement=requirement_agreement_bin,
            disability=disability_bin,
            indigenous=indigenous_bin,
            annual_income=form.get("annualIncome"),
            enrollment_chance=None,
            age_at_enrollment=age_at_enrollment
        )
        student.save()
        # After saving, compute probability (model inference) and export feature JSON (best-effort)
        # Note: compute_and_save_enrollment_chance() persists the probability to student.enrollment_chance
        try:
            probability = compute_and_save_enrollment_chance(student)
        except Exception:
            probability = None
        try:
            feature_path = write_feature_json(student)
        except Exception:
            feature_path = None
        # Instead of showing a separate results page, return to the registration
        # screen with a success/loading modal and a button to go to Home.
        # Keep context minimal; UI does not display model details now.
        return render(
            request,
            "registration.html",
            {
                "submission_success": True,
            },
        )

    return render(request, "registration.html")

# Optional future improvement:
# Instead of calling compute_and_save_enrollment_chance inside the view, you can
# move this logic to a Django post_save signal for Student so every creation (or
# update meeting certain criteria) automatically refreshes the enrollment_chance.
# Example skeleton (place in signals.py and import in apps.py ready()):
#
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Student
# from .ml_utils import compute_and_save_enrollment_chance
#
# @receiver(post_save, sender=Student)
# def update_enrollment_chance(sender, instance, created, **kwargs):
#     if created and instance.enrollment_chance is None:
#         compute_and_save_enrollment_chance(instance)