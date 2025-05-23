# Generated by Django 5.1.4 on 2025-04-28 10:16

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0003_alter_invitation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
        migrations.AddField(
            model_name='usercompany',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True),
        ),
    ]
