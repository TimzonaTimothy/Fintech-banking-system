# Generated by Django 3.2 on 2023-08-19 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_kyc_signature_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='kyc',
            name='kyc_confirmed',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='kyc',
            name='kyc_submitted',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
