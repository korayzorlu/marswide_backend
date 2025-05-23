# Generated by Django 5.1.4 on 2025-03-28 20:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_alter_importprocess_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importprocess',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='pending', max_length=25, null=True, verbose_name='Status'),
        ),
    ]
