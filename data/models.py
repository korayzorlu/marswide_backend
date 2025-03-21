from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Country(models.Model):
    name = models.CharField(_("Name"), max_length=150, blank=True, null=True)
    formal_name = models.CharField(_("Formal Name"), max_length=150, blank=True, null=True)
    iso2 = models.CharField(_("iso2"), max_length=15, blank=True, null=True)
    iso3 = models.CharField(_("iso3"), max_length=15, blank=True, null=True)
    dial_code = models.CharField(_("Dial Code"), max_length=15, blank=True, null=True)
    emoji = models.CharField(_("Emoji"), max_length=15, blank=True, null=True)
    flag = models.CharField(_("Flag"), max_length=150, blank=True, null=True)
    #afg old flag: https://flagcdn.com/af.svg
    
    created_date = models.DateTimeField(auto_now_add=True, null=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name}"