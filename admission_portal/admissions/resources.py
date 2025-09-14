import datetime
from import_export import resources, fields
from .models import Student


class StudentResource(resources.ModelResource):
    # Map Excel headers -> Django model fields
    id = fields.Field(attribute="id", column_name="ID")
    student_id = fields.Field(attribute="student_id", column_name="Student ID")
    school_year = fields.Field(attribute="school_year", column_name="School Year")
    school_term = fields.Field(attribute="school_term", column_name="School Term")
    campus_code = fields.Field(attribute="campus_code", column_name="Campus Code")
    program_first_choice = fields.Field(attribute="program_first_choice", column_name="Program (First Choice)")
    program_second_choice = fields.Field(attribute="program_second_choice", column_name="Program (Second Choice)")
    birth_date = fields.Field(attribute="birth_date", column_name="Birth Date")
    birth_place = fields.Field(attribute="birth_place", column_name="Birth Place")
    birth_city = fields.Field(attribute="birth_city", column_name="Birth City")
    place_of_birth_province = fields.Field(attribute="place_of_birth_province", column_name="Place of Birth (Province)")
    gender = fields.Field(attribute="gender", column_name="Gender")
    citizen_of = fields.Field(attribute="citizen_of", column_name="Citizen of")
    religion = fields.Field(attribute="religion", column_name="Religion")
    civil_status = fields.Field(attribute="civil_status", column_name="Civil Status")
    current_region = fields.Field(attribute="current_region", column_name="Current Region")
    current_province = fields.Field(attribute="current_province", column_name="Current Province")
    city_municipality = fields.Field(attribute="city_municipality", column_name="City/Municipality")
    current_brgy = fields.Field(attribute="current_brgy", column_name="Current Brgy.")
    current_street = fields.Field(attribute="current_street", column_name="Current Street")
    current_postal_code = fields.Field(attribute="current_postal_code", column_name="Current Postal Code")
    complete_present_address = fields.Field(attribute="complete_present_address", column_name="Complete Present Address")
    telephone_no = fields.Field(attribute="telephone_no", column_name="Telephone No.")
    mobile_number = fields.Field(attribute="mobile_number", column_name="Mobile Number")
    email = fields.Field(attribute="email", column_name="Email")
    permanent_country = fields.Field(attribute="permanent_country", column_name="Permanent Country")
    permanent_region = fields.Field(attribute="permanent_region", column_name="Permanent Region")
    permanent_province = fields.Field(attribute="permanent_province", column_name="Permanent Province")
    permanent_city = fields.Field(attribute="permanent_city", column_name="Permanent City")
    permanent_brgy = fields.Field(attribute="permanent_brgy", column_name="Permanent Brgy.")
    permanent_street = fields.Field(attribute="permanent_street", column_name="Permanent Street")
    permanent_postal_code = fields.Field(attribute="permanent_postal_code", column_name="Permanent Postal Code")
    complete_permanent_address = fields.Field(attribute="complete_permanent_address", column_name="Complete Permanent Address")
    disability = fields.Field(attribute="disability", column_name="Disability")
    indigenous = fields.Field(attribute="indigenous", column_name="Indigenous")
    birth_country = fields.Field(attribute="birth_country", column_name="Birth Country")
    requirement_agreement = fields.Field(attribute="requirement_agreement", column_name="Requirement Agreement")
    student_type = fields.Field(attribute="student_type", column_name="Student Type")
    last_school_attended = fields.Field(attribute="last_school_attended", column_name="Last School Attended")
    school_type = fields.Field(attribute="school_type", column_name="School Type")
    enrolled = fields.Field(attribute="enrolled", column_name="Enrolled")

    def clean_birth_date(self, value):
        """Convert Excel value to Python date."""
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, str) and value.strip():
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
                try:
                    return datetime.datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    def before_import_row(self, row, **kwargs):
        row["Birth Date"] = self.clean_birth_date(row.get("Birth Date"))

    def skip_row(self, instance, original, row, import_validation_errors=None):
        # Skip rows with missing Student ID
        if not instance.student_id:
            return False
        # Skip duplicates by email if email already exists
        if instance.email and Student.objects.filter(email=instance.email).exists():
            return False
        return False
        
    class Meta:
        model = Student
        import_id_fields = ()
        skip_unchanged = False
        report_skipped = False
