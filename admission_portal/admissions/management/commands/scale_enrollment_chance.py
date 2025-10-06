from django.core.management.base import BaseCommand
from admissions.models import Student

class Command(BaseCommand):
    help = "Scale enrollment_chance values stored as probabilities (<=1) to percentages (0..100)."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only report what would change.')
        parser.add_argument('--verbose', action='store_true', help='List each scaled record.')

    def handle(self, *args, **options):
        dry = options['dry_run']
        verbose = options['verbose']
        qs = Student.objects.exclude(enrollment_chance__isnull=True)
        to_scale = qs.filter(enrollment_chance__lte=1.0000001)
        count = to_scale.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No probability-style values found; nothing to scale.'))
            return
        self.stdout.write(f'Found {count} enrollment_chance values <= 1.0 to scale.')
        changed = 0
        for s in to_scale.iterator():
            old = s.enrollment_chance
            new = old * 100.0
            if verbose or dry:
                self.stdout.write(f'ID {s.id}: {old:.6f} -> {new:.2f}{" (dry-run)" if dry else ""}')
            if not dry:
                Student.objects.filter(pk=s.pk).update(enrollment_chance=new)
                changed += 1
        if not dry:
            self.stdout.write(self.style.SUCCESS(f'Scaled {changed} rows.'))
        else:
            self.stdout.write(self.style.WARNING('Dry run complete; no changes written.'))
