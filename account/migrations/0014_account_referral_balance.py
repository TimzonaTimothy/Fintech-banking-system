# Generated by Django 3.2 on 2023-08-20 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0013_alter_notification_message_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='referral_balance',
            field=models.FloatField(blank=True, default=0.0, null=True),
        ),
    ]