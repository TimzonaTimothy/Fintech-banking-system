# Generated by Django 3.2 on 2023-08-28 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_alter_transaction_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('Payment', 'Payment'), ('Bill', 'Bill')], max_length=100, null=True),
        ),
    ]
