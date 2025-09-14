# admissions/views.py
from django.shortcuts import render, redirect
from .models import Student
from django.contrib.auth import authenticate, login
from django.contrib import messages


def index(request):
    return render(request, 'index.html')

def loginAdmin(request):
    return render(request, 'login.html')

def adminLanding(request):
    return render(request, 'admin.html')

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
            requirement_agreement=True if truthful_info and data_privacy else False
        )
        student.save()
        return redirect("index")  # redirect to homepage after success

    return render(request, "registration.html")
