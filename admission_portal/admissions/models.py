from django.db import models

class Student(models.Model):
    school_year = models.CharField(max_length=10, blank=True, null=True)
    school_term = models.CharField(max_length=10, blank=True, null=True)
    campus_code = models.CharField(max_length=10, blank=True, null=True)
    program_first_choice = models.CharField(max_length=100, blank=True, null=True)
    program_second_choice = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=100, blank=True, null=True)
    birth_city = models.CharField(max_length=100, blank=True, null=True)
    birth_province = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    citizen_of = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    civil_status = models.CharField(max_length=50, blank=True, null=True)
    
    current_region = models.CharField(max_length=100, blank=True, null=True)
    current_province = models.CharField(max_length=100, blank=True, null=True)
    current_city = models.CharField(max_length=100, blank=True, null=True)
    current_brgy = models.CharField(max_length=100, blank=True, null=True)
    current_street = models.CharField(max_length=255, blank=True, null=True)
    current_postal_code = models.CharField(max_length=10, blank=True, null=True)
    complete_present_address = models.TextField(blank=True, null=True)

    telephone_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=False, blank=True, null=True)

    permanent_country = models.CharField(max_length=100, blank=True, null=True)
    permanent_region = models.CharField(max_length=100, blank=True, null=True)
    permanent_province = models.CharField(max_length=100, blank=True, null=True)
    permanent_city = models.CharField(max_length=100, blank=True, null=True)
    permanent_brgy = models.CharField(max_length=100, blank=True, null=True)
    permanent_street = models.CharField(max_length=255, blank=True, null=True)
    permanent_postal_code = models.CharField(max_length=10, blank=True, null=True)
    complete_permanent_address = models.TextField(blank=True, null=True)

    student_id = models.CharField(max_length=20, unique=False, blank=True, null=True)
    disability = models.CharField(max_length=100, blank=True, null=True)
    indigenous = models.CharField(max_length=100, blank=True, null=True)
    birth_country = models.CharField(max_length=100, blank=True, null=True)
    requirement_agreement = models.BooleanField(default=False, null=True)
    student_type = models.CharField(max_length=50, blank=True, null=True)
    last_school_attended = models.CharField(max_length=255, blank=True, null=True)
    school_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.student_id or 'N/A'} - {self.program_first_choice or 'No Program'}"
