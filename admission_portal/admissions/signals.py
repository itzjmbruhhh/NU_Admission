from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student

@receiver(post_save, sender=Student)
def ensure_enrollment_chance_percentage(sender, instance: Student, created, **kwargs):
    """Ensure enrollment_chance is stored as percentage (0..100).
    If value looks like a probability (<=1), scale it x100.
    Runs after every save; uses update_fields to avoid recursion.
    """
    val = instance.enrollment_chance
    if val is None:
        return
    # If it's clearly a probability (<=1.0), scale
    if val <= 1.0000001:
        instance.enrollment_chance = float(val) * 100.0
        # Avoid triggering infinite loop by saving only that field
        Student.objects.filter(pk=instance.pk).update(enrollment_chance=instance.enrollment_chance)
