from django.test import TestCase
from .models import Student
from .utils import write_feature_json
import json

class FeatureExportTests(TestCase):
    def test_feature_json_creation(self):
        student = Student.objects.create(
            school_term='1',
            program_first_choice='CS',
            program_second_choice='IT',
            entry_level='Freshman',
            birth_city='CityX',
            birth_province='ProvinceX',
            gender='Male',
            citizen_of='CountryX',
            religion='ReligionX',
            civil_status='Single',
            current_region='RegionX',
            current_province='ProvinceX',
            current_city='CityX',
            current_brgy='BrgyX',
            permanent_country='CountryX',
            permanent_region='RegionY',
            permanent_province='ProvinceY',
            permanent_city='CityY',
            permanent_brgy='BrgyY',
            birth_country='CountryX',
            student_type='New',
            school_type='Public',
            requirement_agreement=1,
            disability=0,
            indigenous=0,
        )
        path = write_feature_json(student)
        self.assertTrue(path.exists())
        data = json.loads(path.read_text())
        # Expect a single dummy_Student{pk} key
        key = f'dummy_Student{student.pk}'
        self.assertIn(key, data)
        record = data[key]
        # Spot check required fields
        for field in ['ID','Program (First Choice)','Entry Level','Birth City','Disability','Indigenous','Requirement Agreement']:
            self.assertIn(field, record)
        self.assertEqual(record['ID'], student.pk)
