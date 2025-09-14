from django.db import models

class Student(models.Model):
    school_year = models.CharField(max_length=10)
    school_term = models.CharField(max_length=10)
    campus_code = models.CharField(max_length=10)
    program_first_choice = models.CharField(max_length=100)
    program_second_choice = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=100)
    birth_city = models.CharField(max_length=100)
    birth_province = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    citizen_of = models.CharField(max_length=100)
    religion = models.CharField(max_length=100, blank=True, null=True)
    civil_status = models.CharField(max_length=50)
    
    current_region = models.CharField(max_length=100)
    current_province = models.CharField(max_length=100)
    current_city = models.CharField(max_length=100)
    current_brgy = models.CharField(max_length=100)
    current_street = models.CharField(max_length=255)
    current_postal_code = models.CharField(max_length=10)
    complete_present_address = models.TextField()

    telephone_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    permanent_country = models.CharField(max_length=100)
    permanent_region = models.CharField(max_length=100)
    permanent_province = models.CharField(max_length=100)
    permanent_city = models.CharField(max_length=100)
    permanent_brgy = models.CharField(max_length=100)
    permanent_street = models.CharField(max_length=255)
    permanent_postal_code = models.CharField(max_length=10)
    complete_permanent_address = models.TextField()

    student_id = models.CharField(max_length=20, unique=True)
    disability = models.CharField(max_length=100, blank=True, null=True)
    indigenous = models.CharField(max_length=100, blank=True, null=True)
    birth_country = models.CharField(max_length=100)
    requirement_agreement = models.BooleanField(default=False)
    student_type = models.CharField(max_length=50)
    last_school_attended = models.CharField(max_length=255, blank=True, null=True)
    school_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.student_id} - {self.program_first_choice}"
