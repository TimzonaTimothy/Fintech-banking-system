# Generated by Django 3.2 on 2023-08-25 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='crypto',
            old_name='signature_image',
            new_name='transaction_image',
        ),
    ]