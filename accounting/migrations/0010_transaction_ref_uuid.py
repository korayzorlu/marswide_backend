# Generated by Django 5.1.4 on 2025-04-29 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0009_invoice_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='ref_uuid',
            field=models.CharField(default=1, max_length=140, unique=True, verbose_name='Ref UUID'),
            preserve_default=False,
        ),
    ]
