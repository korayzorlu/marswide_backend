# Generated by Django 5.1.4 on 2025-05-01 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partners', '0018_alter_partner_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='name',
            field=models.CharField(max_length=140, verbose_name='Partner Name'),
        ),
    ]
