from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from .models import *

# class UserAdmin(admin.ModelAdmin):
#     model = User
#     list_display = ['email', 'first_name', 'last_name', 'is_active']

admin.site.register(User, UserAdmin)
#admin.site.register(Profile)