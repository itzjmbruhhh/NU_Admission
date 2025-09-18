from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('admissions', '0013_student_annual_income'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='age_at_enrollment',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
