# Generated by Django 3.2 on 2023-08-18 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_account_recommend_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_restricted',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
