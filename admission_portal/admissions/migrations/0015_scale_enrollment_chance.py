from django.db import migrations


def forward(apps, schema_editor):
    Student = apps.get_model('admissions', 'Student')
    # Scale probabilities (<=1) to percentages
    qs = Student.objects.exclude(enrollment_chance__isnull=True)
    for s in qs.iterator():
        val = s.enrollment_chance
        if val is not None and val <= 1.0000001:
            s.enrollment_chance = val * 100.0
            s.save(update_fields=['enrollment_chance'])


def backward(apps, schema_editor):
    Student = apps.get_model('admissions', 'Student')
    qs = Student.objects.exclude(enrollment_chance__isnull=True)
    for s in qs.iterator():
        val = s.enrollment_chance
        # Only divide if clearly a percentage
        if val is not None and 1.0 < val <= 100.0:
            s.enrollment_chance = val / 100.0
            s.save(update_fields=['enrollment_chance'])


class Migration(migrations.Migration):
    dependencies = [
        ('admissions', '0014_student_age_at_enrollment'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
