from django.contrib import admin

from .models import *

# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["user","name", "formal_name"]
    list_display_links = ["name"]
    search_fields = ["user__email","name","formal_name"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def user(self,obj):
        return obj.user.email if obj.user else ""
    
    class Meta:
        model = Company

@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    list_display = ["user","company", "is_active", "is_admin"]
    list_display_links = ["company"]
    search_fields = ["user__email","company__name","is_active","is_admin"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def user(self,obj):
        return obj.user.email if obj.user else ""
    
    def company(self,obj):
        return obj.company.name if obj.company else ""
    
    class Meta:
        model = UserCompany

