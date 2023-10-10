from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets
from django.contrib.auth import get_user_model
from .models import Transaction
User = get_user_model()

def get_unique_string(length=8, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    while True:
        code = ''.join(secrets.choice(allowed_chars) for _ in range(length))
        if not User.objects.filter(code=code).exists():
            return code

def get_unique_trn_id(length=10, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    while True:
        code = ''.join(secrets.choice(allowed_chars) for _ in range(length))
        if not Transaction.objects.filter(transaction_id=code).exists():
            return 'TX'+ code

def generate_ref_code(sender, instance, created, **kwargs):
    if created and not instance.code:
        instance.code = get_unique_string()
        instance.save()

def generate_transaction_id(sender, instance, created, **kwargs):
    if created and not instance.transaction_id:
        instance.transaction_id = get_unique_trn_id()
        instance.save()


post_save.connect(generate_ref_code, sender=User)
post_save.connect(generate_transaction_id, sender=Transaction)

