from django.contrib import admin

from .models import *

# Register your models here.

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name","formal_name","iso2","iso3","dial_code"]
    list_display_links = ["name"]
    search_fields = ["name","formal_name","iso2","iso3","dial_code"]
    list_filter = []
    inlines = []
    ordering = ["id"]
    
    class Meta:
        model = Country