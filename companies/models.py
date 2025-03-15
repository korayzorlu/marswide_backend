from django.db import models

from django.utils.translation import gettext_lazy as _

from users.models import User

# Create your models here.

def get_sentinel_user():
    return User.objects.get_or_create(username="unknown")[0]

class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), blank = True, null = True, related_name="company")
    name = models.CharField(_("Company Name"), max_length=140)
    formal_name = models.CharField(_("Company Formal Name"), max_length=140, blank = True, null=True)
    image = models.ImageField(_("Image"), upload_to='media/docs/companies/ ', null=True, blank=True,
                              help_text=_("Please upload a square image, otherwise center will be cropped."))
    
    def save(self, *args, **kwargs):
        if self.formal_name is None:
            self.formal_name = self.name
        super(Company, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)
    
class UserCompany(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_companies")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_users")
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'company')  # Aynı kullanıcı aynı şirkete birden fazla kez atanamaz.


    def __str__(self):
        return str(self.company.name)
    
class Invitation(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="taken_invitations")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invitations")

    STATUS_CHOICES = (
        ('pending', ('Pending')),
        ('accepted', ('Accepted')),
        ('declined', ('Declined'))
    )
    status = models.CharField(_("Theme"), max_length=25, default='pending', choices=STATUS_CHOICES, blank=True, null=True)

    token = models.CharField(max_length=255, unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.recipient} - {self.company.name} ({self.status})"