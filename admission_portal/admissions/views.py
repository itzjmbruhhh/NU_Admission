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

    students = Student.objects.all()
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
    }
    return render(request, 'admin.html', context)

def register(request):
    return render(request, 'registration.html')

def register_student(request):
    if request.method == "POST":
        # Grab form data by name attributes
        school_year = request.POST.get("schoolYear")
        school_term = request.POST.get("schoolTerm")
        campus = request.POST.get("campus")
        first_choice = request.POST.get("firstChoice")
        second_choice = request.POST.get("secondChoice")
        student_type = request.POST.get("studentType")
        first_name = request.POST.get("firstName")
        last_name = request.POST.get("lastName")
        middle_name = request.POST.get("middleName")
        suffix = request.POST.get("suffix")
        gender = request.POST.get("gender")
        civil_status = request.POST.get("civilStatus")
        birth_date = request.POST.get("birthDate")
        birth_place = request.POST.get("birthPlace")
        nationality = request.POST.get("nationality")
        religion = request.POST.get("religion")
        present_address = request.POST.get("presentAddress")
        city_province = request.POST.get("cityProvince")
        zip_code = request.POST.get("zipCode")
        mobile_number = request.POST.get("mobileNumber")
        email = request.POST.get("emailAddress")
        father_name = request.POST.get("fatherName")
        father_occupation = request.POST.get("fatherOccupation")
        mother_name = request.POST.get("motherName")
        mother_occupation = request.POST.get("motherOccupation")
        guardian_contact = request.POST.get("guardianContact")
        truthful_info = request.POST.get("truthfulInfo")
        data_privacy = request.POST.get("dataPrivacy")

        # Save to DB (adjust field names according to your Student model)
        student = Student.objects.create(
            school_year=school_year,
            school_term=school_term,
            campus_code=campus,
            program_first_choice=first_choice,
            program_second_choice=second_choice,
            student_type=student_type,
            # add other fields here...
            email=email,
            mobile_number=mobile_number,
            religion=religion,
            gender=gender,
            civil_status=civil_status,
            birth_date=birth_date,
            birth_place=birth_place,
            citizen_of=nationality,
            complete_present_address=present_address,
            current_city=city_province,
            current_postal_code=zip_code,
            last_school_attended="",  # optional for now
            requirement_agreement=True if truthful_info and data_privacy else False,
            enrolled=""
        )
        student.save()
        return redirect("index")  # redirect to homepage after success

    return render(request, "registration.html")