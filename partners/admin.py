from django.contrib import admin

from .models import Partner

# Register your models here.

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ["company","name", "formal_name"]
    list_display_links = ["name"]
    search_fields = ["company__name","name","formal_name"]
    list_filter = []
    inlines = []
    ordering = ["-id"]
    
    def company(self,obj):
        return obj.company.name if obj.company else ""
    
    class Meta:
        model = Partner