from django.db import models

from django.utils.translation import gettext_lazy as _

from companies.models import Company

# Create your models here.

class Partner(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="partners")
    name = models.CharField(_("Partner Name"), max_length=140)
    formal_name = models.CharField(_("Partner Formal Name"), max_length=140, blank = True, null=True)
    image = models.ImageField(_("Image"), upload_to='media/docs/companies/ ', null=True, blank=True,
                              help_text=_("Please upload a square image, otherwise center will be cropped."))
    
    def save(self, *args, **kwargs):
        if self.formal_name is None:
            self.formal_name = self.name
        super(Partner, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)