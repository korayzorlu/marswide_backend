from django.contrib import admin
from django import forms

from .models import Account

# Register your models here.



@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ["company","partner","type","currency","balance"]
    list_display_links = ["partner"]
    search_fields = ["company__name","partner__name","type","currency__code","balance"]
    list_filter = []
    inlines = []
    ordering = ["company__name","partner__name"]
    
    def company(self,obj):
        return obj.company.name if obj.company else ""
    def partner(self,obj):
        return obj.partner.name if obj.partner else ""
    def currency(self,obj):
        return obj.currency.code if obj.currency else ""
    
    class Meta:
        model = Account
