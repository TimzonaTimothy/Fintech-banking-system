# Generated by Django 3.2 on 2023-08-20 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_notification_message_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='message_type',
            field=models.CharField(blank=True, choices=[('Sent', 'Sent'), ('Recieved', 'Recieved'), ('Password_Change', 'Password_Change'), ('Message', 'Message')], max_length=100, null=True),
        ),
    ]