# Generated by Django 5.1.4 on 2025-05-13 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0016_alter_transaction_ref_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='receiver',
            field=models.CharField(choices=[('bank', 'Bank'), ('cash', 'Cash')], default='bank', max_length=10, verbose_name='Receiver'),
        ),
    ]
