# Generated by Django 3.2 on 2023-08-20 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20230820_1835'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='message_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
