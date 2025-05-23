# Generated by Django 5.1.4 on 2025-04-26 04:54

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0005_account_unique_partner_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('type', models.CharField(choices=[('debit', 'Debit'), ('credit', 'Credit')], default='debit', max_length=10, verbose_name='Type')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=14, verbose_name='Amount')),
                ('date', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_transactions', to='accounting.account')),
            ],
        ),
    ]
