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

    TYPES = [
        ('receivable', 'Receivable'),
        ('payable', 'Payable')
    ]
    type = models.CharField(_("Type"), max_length=10, choices=TYPES, default = "receivable")

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="partner_accounts")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, blank=True, null=True, related_name="partner_accounts")

    balance = models.DecimalField(_("Balance"), default = 0.00, max_digits=14, decimal_places=2)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['partner', 'currency'], name='unique_partner_currency')
        ]

    def __str__(self):
        return str(self.partner.name)