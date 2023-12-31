# Generated by Django 3.2 on 2023-08-26 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20230825_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='deposit_request',
            name='wallet_id',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='deposit_request',
            name='amount',
            field=models.IntegerField(default='0', null=True),
        ),
        migrations.AlterField(
            model_name='deposit_request',
            name='crypto',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='withdrawal_request',
            name='amount',
            field=models.IntegerField(default='0', null=True),
        ),
    ]
