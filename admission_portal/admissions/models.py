from django.db import models

class Student(models.Model):
    @property
    def get_fields(self):
        """Return all field names and values for admin/template display."""
        return {field.name: getattr(self, field.name) for field in self._meta.fields}

    # Admission Info
    school_year = models.CharField(max_length=10, blank=True, null=True)
    school_term = models.CharField(max_length=10, blank=True, null=True)
    campus_code = models.CharField(max_length=50, blank=True, null=True)
    program_first_choice = models.CharField(max_length=100, blank=True, null=True)
    program_second_choice = models.CharField(max_length=100, blank=True, null=True)
    entry_level = models.CharField(max_length=50, blank=True, null=True)

    # Personal Info
    full_name = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)
    prefix = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=100, blank=True, null=True)
    birth_city = models.CharField(max_length=100, blank=True, null=True)
    birth_province = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    citizen_of = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=100, blank=True, null=True)
    civil_status = models.CharField(max_length=50, blank=True, null=True)
    birth_country = models.CharField(max_length=100, blank=True, null=True)

    # Contact Info
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

    # Student Info
    student_id = models.CharField(max_length=20, blank=True, null=True)
    disability = models.CharField(max_length=100, blank=True, null=True)
    indigenous = models.CharField(max_length=100, blank=True, null=True)
    requirement_agreement = models.CharField(default=False, null=True)
    student_type = models.CharField(max_length=50, blank=True, null=True)
    last_school_attended = models.CharField(max_length=255, blank=True, null=True)
    school_type = models.CharField(max_length=50, blank=True, null=True)


    # Additional Fields
    annual_income = models.CharField(max_length=50, blank=True, null=True)
    enrollment_chance = models.FloatField(blank=True, null=True)
    # Computed once at registration time
    age_at_enrollment = models.IntegerField(blank=True, null=True)
    
    @property
    def status(self):
        return "Enrolled" if self.student_id else "Not Enrolled"

    @property
    def enrollment_chance_display(self):
        """Return formatted enrollment chance e.g. 'Enrollment chance: 72.35%'."""
        if self.enrollment_chance is None:
            return "Enrollment chance: N/A"
        return f"Enrollment chance: {self.enrollment_chance * 100:.2f}%"

    def save(self, *args, **kwargs):
        """Automatically update status based on student_id if not manually set."""
        if not self.status:
            self.status = "Enrolled" if self.student_id else "Not Enrolled"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id or 'N/A'} - {self.full_name or self.program_first_choice or 'No Name'}"
    