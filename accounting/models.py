from django.db import models

from django.utils.translation import gettext_lazy as _
import uuid

from partners.models import Partner
from common.models import Currency
from companies.models import Company

# Create your models here.

class Account(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="accounts")

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="partner_accounts")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="partner_accounts")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)