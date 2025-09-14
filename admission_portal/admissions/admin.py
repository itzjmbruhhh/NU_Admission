from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Student
from .resources import StudentResource

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
