from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets
from django.contrib.auth import get_user_model
from .models import Deposit_Request

def get_unique_string(length=15, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    while True:
        code = ''.join(secrets.choice(allowed_chars) for _ in range(length))
        if not Deposit_Request.objects.filter(reference_id=code).exists():
            return code

def generate_ref_code(sender, instance, created, **kwargs):
    if created and not instance.reference_id:
        instance.reference_id = get_unique_string()
        instance.save()

post_save.connect(generate_ref_code, sender=Deposit_Request)

