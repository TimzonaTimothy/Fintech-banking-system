# Generated by Django 3.2 on 2023-10-02 12:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0029_alter_account_pin'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDevice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(max_length=255, null=True)),
                ('device_type', models.CharField(max_length=255, null=True)),
                ('device_os', models.CharField(max_length=255, null=True)),
                ('device_browser', models.CharField(max_length=255, null=True)),
                ('last_login', models.DateTimeField(null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='chatMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, null=True)),
                ('user_from', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user_to', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-date_created',),
            },
        ),
    ]
