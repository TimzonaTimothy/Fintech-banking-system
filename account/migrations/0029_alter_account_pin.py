# Generated by Django 3.2 on 2023-09-26 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0028_alter_account_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='pin',
            field=models.CharField(blank=True, max_length=4, null=True, unique=True, verbose_name='PIN CODE'),
        ),
    ]