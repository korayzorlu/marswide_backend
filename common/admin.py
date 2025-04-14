from django.contrib import admin

from .models import *

# Register your models here.

@admin.register(ImportProcess)
class ImportProcessAdmin(admin.ModelAdmin):
    list_display = ["task_id","status","user","model_name","created_date"]
    list_display_links = ["task_id"]
    search_fields = ["task_id","status","user__email","model_name","created_date"]
    list_filter = []
    inlines = []
    ordering = ["-id"]

    def user(self,obj):
        return obj.user.email if obj.user else ""
    
    class Meta:
        model = ImportProcess