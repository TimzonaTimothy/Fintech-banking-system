# Generated by Django 3.2 on 2023-08-25 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Crypto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crypto', models.CharField(blank=True, max_length=100, null=True)),
                ('amount', models.IntegerField(blank=True, default='0', null=True)),
                ('reference_id', models.CharField(blank=True, max_length=500, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=500, null=True)),
                ('signature_image', models.ImageField(blank=True, upload_to='useridentity/%Y%m%d/')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('added_to_balance', models.BooleanField(default=False, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Fund Deposit',
                'verbose_name_plural': 'Fund Deposits',
            },
        ),
    ]