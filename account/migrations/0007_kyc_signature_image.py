# Generated by Django 3.2 on 2023-08-18 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_account_is_restricted'),
    ]

    operations = [
        migrations.AddField(
            model_name='kyc',
            name='signature_image',
            field=models.ImageField(blank=True, upload_to='useridentity/%Y%m%d/'),
        ),
    ]
