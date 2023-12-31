# Generated by Django 3.2 on 2023-08-30 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0023_remove_account_account_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='account',
            name='two_step_verification',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
