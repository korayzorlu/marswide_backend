from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    """
    This model represents the profile info of Internal Personals.
    """
    THEME_CHOICES = (('dark', ('Dark')), ('light', ('Light')))
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, blank=True)
    
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.user} | {self.user.get_full_name()}"


