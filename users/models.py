from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True) 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name','last_name']

# class Profile(models.Model):
#     """
#     This model represents the profile info of Internal Personals.
#     """
    
#     user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, blank=True)

#     THEME_CHOICES = (('dark', ('Dark')), ('light', ('Light')))
#     theme = models.CharField(_("Theme"), max_length=25, default='light', choices=THEME_CHOICES, blank=True, null=True)
    
    
#     created_at = models.DateTimeField(auto_now_add=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True, null=True)

#     def __str__(self):
#         return f"{self.user} | {self.user.get_full_name()}"