# Generated by Django 5.1.4 on 2025-02-06 10:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ImageField(blank=True, help_text='Please upload a square image, otherwise center will be cropped.', null=True, upload_to='media/docs/users/ ', verbose_name='Image'),
        ),
    ]
