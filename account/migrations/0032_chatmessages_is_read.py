# Generated by Django 3.2 on 2023-10-04 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0031_chatmessages_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessages',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
