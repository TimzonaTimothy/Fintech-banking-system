# Generated by Django 3.2 on 2023-08-17 23:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_account_re_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='re_by',
        ),
    ]